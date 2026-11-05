#!/usr/bin/env python3
"""Custo e checagens das sessões reais da Trilha de Estudos, por modelo.

Uso:
  python3 harness/medir.py                 # mostra as sessões e as checagens
  python3 harness/medir.py --registrar     # também salva em harness/sessoes.json
                                           # e atualiza avaliacao-modelos.md
  python3 harness/medir.py --incluir ARQ.jsonl   # sessão aberta fora da pasta da trilha

Lê os logs do Claude Code em ~/.claude/projects/-home-...-TrilhaDeEstudos/.
Só entra aqui o que foi aberto com `cd ~/Desktop/TrilhaDeEstudos && claude`.
O Claude Code apaga logs com mais de 30 dias, por isso o --registrar guarda
cada sessão em harness/sessoes.json e nunca apaga o que já está lá.

Cada mensagem do Rafael abre um turno. O turno conta como "outro" (e fica fora
do custo de estudo) quando usa pesquisa na web, subagente ou workflow, roda git
ou gh, ou mexe no harness, no CLAUDE.md ou no avaliacao-modelos.md. O resto é
estudo. Turno só de texto que não foi estudo (ex.: redigir um post) não tem como
ser detectado: marque à mão com --outro SESSAO:N, usando o número de --turnos.

Custo em dólar a preço de API (tabela PRECOS abaixo, conferida na página oficial em 05/11/2026). O plano
cobra em limite de uso e não em dólar, então o valor serve para comparar
modelos. A coluna "a preço de Opus" aplica o preço do Opus aos mesmos tokens,
o que é aproximado: outro modelo gastaria um número um pouco diferente de tokens.
"""

import argparse
import datetime
import glob
import json
import os
import re
import sys

HARNESS = os.path.dirname(os.path.abspath(__file__))
TRILHA = os.path.dirname(HARNESS)
LOGS = os.path.join(os.path.expanduser("~/.claude/projects"), TRILHA.replace("/", "-"))
SESSOES = os.path.join(HARNESS, "sessoes.json")
AVALIACAO = os.path.join(TRILHA, "avaliacao-modelos.md")

# US$ por milhão de tokens: entrada, leitura de cache, saída.
# Gravação de cache: 2x a entrada (TTL de 1 hora) ou 1,25x (TTL de 5 minutos).
PRECOS = {
    "opus": (4.00, 0.20, 20.00),
    "sonnet": (2.00, 0.10, 10.00),  # leitura de cache a 0,05x no Opus 5.5 e no Sonnet 5.5
    "haiku": (0.10, 0.01, 0.50),  # até 100 mil tokens de prompt; acima disso, 5x
    "fable": (10.00, 0.25, 50.00),
}
PESQUISA = {"WebSearch", "WebFetch", "Agent", "Workflow"}
CONFIG = {"CLAUDE.md", "avaliacao-modelos.md", ".gitignore"}
AJUSTES = os.path.join(HARNESS, "ajustes.json")
INICIO_COMPARACAO = datetime.date(2026, 11, 5)
TRACOS = re.compile("[–—]")


def familia(modelo):
    for f in PRECOS:
        if f in (modelo or ""):
            return f
    return None


def custo(u, fam):
    if fam is None:
        return 0.0
    entrada, leitura, saida = PRECOS[fam]
    cc = u.get("cache_creation") or {}
    w1h = cc.get("ephemeral_1h_input_tokens", 0)
    w5m = cc.get("ephemeral_5m_input_tokens", u.get("cache_creation_input_tokens", 0) - w1h)
    prompt = u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0)
    fator = 5 if fam == "haiku" and prompt > 100_000 else 1
    total = (u.get("input_tokens", 0) * entrada + w1h * 2 * entrada + w5m * 1.25 * entrada
             + u.get("cache_read_input_tokens", 0) * leitura + u.get("output_tokens", 0) * saida)
    return total * fator / 1e6


def caminho_rel(p):
    p = os.path.abspath(os.path.expanduser(p or ""))
    return os.path.relpath(p, TRILHA) if p.startswith(TRILHA + os.sep) else None


def eh_nota(rel):
    return bool(rel) and rel.endswith(".md") and (rel == "progresso.md" or re.search(r"/\d\d-[^/]+\.md$", rel))


def ler_sessao(arquivo):
    turnos, vistos, atual = [], set(), None
    with open(arquivo, errors="ignore") as f:
        for linha in f:
            try:
                o = json.loads(linha)
            except json.JSONDecodeError:
                continue
            msg = o.get("message") if isinstance(o.get("message"), dict) else {}
            if o.get("type") == "user" and not o.get("isMeta") and not o.get("isCompactSummary"):
                c = msg.get("content")
                if isinstance(c, str) and c.strip() and not c.startswith("<"):
                    atual = {"inicio": o.get("timestamp"), "texto": c.strip()[:70], "chamadas": [],
                             "outro": False, "salvou": False, "python_antes": None}
                    turnos.append(atual)
                continue
            if o.get("type") != "assistant" or atual is None:
                continue
            for b in msg.get("content") or []:
                if not isinstance(b, dict) or b.get("type") != "tool_use":
                    continue
                nome, entrada = b.get("name", ""), b.get("input") or {}
                rel = caminho_rel(entrada.get("file_path"))
                comando = entrada.get("command", "") if nome == "Bash" else ""
                if nome in PESQUISA or "bancada.py" in comando or "claude -p" in comando:
                    atual["outro"] = True
                if re.search(r"(^|[;&|]\s*)(git|gh)\s", comando):
                    atual["outro"] = True
                if nome in {"Write", "Edit"} and (rel is None or rel.startswith("harness/") or rel in CONFIG):
                    atual["outro"] = True
                if "python" in comando and "medir.py" not in comando and atual["python_antes"] is None:
                    atual["python_antes"] = True
                if nome in {"Write", "Edit"} and eh_nota(rel):
                    atual["salvou"] = True
                    if atual["python_antes"] is None:
                        atual["python_antes"] = False
                if comando and re.search(r"(>|tee|sed -i|open\().*?(progresso\.md|\d\d-[\w-]+\.md)", comando):
                    atual["salvou"] = True
            mid, u = msg.get("id"), msg.get("usage")
            if u and mid not in vistos:
                vistos.add(mid)
                atual["chamadas"].append((msg.get("model"), u))
    return turnos


def resumo_sessao(arquivo, ajustes):
    turnos = ler_sessao(arquivo)
    if not turnos:
        return None
    for n in ajustes.get(os.path.basename(arquivo)[:8], []):
        if 1 <= n <= len(turnos):
            turnos[n - 1]["outro"] = True
    saida_por_modelo = {}
    for t in turnos:
        for m, u in t["chamadas"]:
            if familia(m):
                saida_por_modelo[m] = saida_por_modelo.get(m, 0) + u.get("output_tokens", 0)
    if not saida_por_modelo:
        return None
    modelo = max(saida_por_modelo, key=saida_por_modelo.get)

    def soma(lista, preco_de=None):
        return sum(custo(u, preco_de or familia(m)) for t in lista for m, u in t["chamadas"])

    estudo = [t for t in turnos if not t["outro"]]
    outros = [t for t in turnos if t["outro"]]
    salvos = [t for t in estudo if t["salvou"]]
    tokens = {"gravacao_cache": 0, "leitura_cache": 0, "saida": 0}
    for t in estudo:
        for _, u in t["chamadas"]:
            tokens["gravacao_cache"] += u.get("cache_creation_input_tokens", 0)
            tokens["leitura_cache"] += u.get("cache_read_input_tokens", 0)
            tokens["saida"] += u.get("output_tokens", 0)
    inicio = datetime.datetime.fromisoformat(turnos[0]["inicio"].replace("Z", "+00:00")).astimezone()
    return {
        "sessao": os.path.basename(arquivo)[:8],
        "data": inicio.strftime("%Y-%m-%d %H:%M"),
        "modelo": modelo,
        "turnos_estudo": len(estudo),
        "chamadas_estudo": sum(len(t["chamadas"]) for t in estudo),
        "custo_estudo": round(soma(estudo), 4),
        "custo_estudo_preco_opus": round(soma(estudo, "opus"), 4),
        "tokens_estudo": tokens,
        "turnos_outros": len(outros),
        "custo_outros": round(soma(outros), 4),
        "python_antes_de_salvar": f"{sum(bool(t['python_antes']) for t in salvos)}/{len(salvos)}",
        "turnos": [{"texto": t["texto"], "tipo": "outro" if t["outro"] else "estudo",
                    "chamadas": len(t["chamadas"]), "custo": round(soma([t]), 4)} for t in turnos],
    }


def checar_arquivos():
    problemas = []
    for arq in sorted(glob.glob(os.path.join(TRILHA, "**/*.md"), recursive=True)):
        rel = os.path.relpath(arq, TRILHA)
        texto = open(arq, errors="ignore").read()
        for n, linha in enumerate(texto.splitlines(), 1):
            if TRACOS.search(linha):
                problemas.append(f"{rel}:{n} tem travessão ou traço")
        if re.search(r"/\d\d-[^/]+\.md$", rel):
            for secao in ("## Resumo", "## Minhas perguntas", "## Exercícios", "<details>"):
                if secao not in texto:
                    problemas.append(f"{rel} sem '{secao}'")
    progresso = os.path.join(TRILHA, "progresso.md")
    if os.path.exists(progresso):
        partes = re.split(r"(?m)^### ", open(progresso).read())[1:]
        for p in partes:
            titulo = p.splitlines()[0]
            datas = re.findall(r"(\d{2})/(\d{2})/(\d{4})", titulo)
            if not datas:
                continue
            d, m, a = datas[-1]
            if datetime.date(int(a), int(m), int(d)) >= INICIO_COMPARACAO and "**Modelo:**" not in p:
                problemas.append(f"progresso.md: entrada '{titulo}' sem '**Modelo:**'")
    return problemas


def nome_curto(modelo):
    return (modelo or "?").replace("claude-", "").replace("-", " ").title().replace(" 5 5", " 5.5").replace(" 5 1", " 5.1")


def tabela(sessoes):
    linhas = ["| Data | Sessão | Modelo | Turnos de estudo | Custo do estudo (US$) | Por turno | Por turno a preço de Opus | Python antes de salvar | Outros turnos (US$) |",
              "|---|---|---|---|---|---|---|---|---|"]
    for s in sorted(sessoes, key=lambda s: s["data"]):
        n = max(s["turnos_estudo"], 1)
        linhas.append(
            f"| {s['data'][:10]} | {s['sessao']} | {nome_curto(s['modelo'])} | {s['turnos_estudo']} "
            f"| {s['custo_estudo']:.2f} | {s['custo_estudo'] / n:.2f} | {s['custo_estudo_preco_opus'] / n:.2f} "
            f"| {s['python_antes_de_salvar']} | {s['turnos_outros']} ({s['custo_outros']:.2f}) |")
    return "\n".join(linhas)


def substituir(texto, marca, conteudo):
    ini, fim = f"<!-- {marca}:inicio -->", f"<!-- {marca}:fim -->"
    if ini not in texto or fim not in texto:
        return texto
    antes, resto = texto.split(ini, 1)
    return antes + ini + "\n" + conteudo + "\n" + fim + resto.split(fim, 1)[1]


def main():
    ap = argparse.ArgumentParser(description="Custo e checagens das sessões da trilha.")
    ap.add_argument("--registrar", action="store_true")
    ap.add_argument("--incluir", action="append", default=[], help="log .jsonl de sessão aberta fora da trilha")
    ap.add_argument("--turnos", action="store_true", help="mostra cada turno, numerado")
    ap.add_argument("--outro", action="append", default=[], metavar="SESSAO:N",
                    help="marca à mão o turno N da sessão como fora do estudo (fica salvo em harness/ajustes.json)")
    args = ap.parse_args()

    ajustes = json.load(open(AJUSTES)) if os.path.exists(AJUSTES) else {}
    for item in args.outro:
        sessao, n = item.split(":")
        ajustes.setdefault(sessao[:8], [])
        if int(n) not in ajustes[sessao[:8]]:
            ajustes[sessao[:8]].append(int(n))
    if args.outro:
        json.dump(ajustes, open(AJUSTES, "w"), indent=1)

    arquivos = sorted(glob.glob(os.path.join(LOGS, "*.jsonl"))) + [os.path.expanduser(a) for a in args.incluir]
    atuais = [r for r in (resumo_sessao(a, ajustes) for a in arquivos) if r]
    guardadas = json.load(open(SESSOES)) if os.path.exists(SESSOES) else {}
    for s in atuais:
        guardadas[s["sessao"]] = s
    sessoes = list(guardadas.values()) if args.registrar else atuais + [s for k, s in guardadas.items() if k not in {a["sessao"] for a in atuais}]

    print(tabela(sessoes))
    if args.turnos:
        for s in atuais:
            print(f"\n{s['sessao']} ({nome_curto(s['modelo'])})")
            for n, t in enumerate(s["turnos"], 1):
                print(f"  {n:2}. [{t['tipo']:6}] {t['chamadas']:2} chamadas  US$ {t['custo']:.3f}  {t['texto']}")

    problemas = checar_arquivos()
    print("\nChecagens dos arquivos:", "nenhum problema" if not problemas else "")
    for p in problemas:
        print(" -", p)

    if args.registrar:
        json.dump(guardadas, open(SESSOES, "w"), ensure_ascii=False, indent=1)
        if os.path.exists(AVALIACAO):
            texto = open(AVALIACAO).read()
            texto = substituir(texto, "sessoes", tabela(sessoes))
            texto = substituir(texto, "checagens", "Nenhum problema." if not problemas else "\n".join(f"- {p}" for p in problemas))
            open(AVALIACAO, "w").write(texto)
        print(f"\nRegistrado em {os.path.relpath(SESSOES, TRILHA)} e avaliacao-modelos.md")


if __name__ == "__main__":
    sys.exit(main())
