#!/usr/bin/env python3
"""Bancada: a mesma prova de correção para cada modelo, com nota automática.

Cada caso de harness/casos.json traz um exercício e uma resposta do aluno com
erros plantados. O modelo corrige como tutor da trilha e devolve um JSON por
item, que é comparado com o gabarito. Mede o que as pesquisas apontam como o
ponto fraco de modelo menor: achar o erro do aluno sem inventar erro onde não tem.

Uso:
  python3 harness/bancada.py                          # opus, sonnet e haiku, 2 rodadas
  python3 harness/bancada.py --modelos sonnet
  python3 harness/bancada.py --modelos opus,sonnet --rodadas 1 --casos C1,C7
  python3 harness/bancada.py --esforco high

Roda `claude -p` sem ferramentas, sem MCP e sem salvar sessão, numa pasta
temporária vazia. Gasta do limite do plano: no teste de 05/11/2026 a prova
inteira custou o equivalente a poucos centavos de dólar no Haiku e por volta
de US$ 1 no Opus. O custo mostrado é o que o Claude Code calcula a preço de API.

Resultados completos (com as explicações) vão para harness/resultados/ e uma
linha de resumo por modelo entra na tabela da bancada em avaliacao-modelos.md.
"""

import argparse
import concurrent.futures
import datetime
import json
import os
import re
import subprocess
import sys
import tempfile

HARNESS = os.path.dirname(os.path.abspath(__file__))
TRILHA = os.path.dirname(HARNESS)
CASOS = os.path.join(HARNESS, "casos.json")
RESULTADOS = os.path.join(HARNESS, "resultados")
AVALIACAO = os.path.join(TRILHA, "avaliacao-modelos.md")
MARCA_FIM = "<!-- bancada:fim -->"

PROMPT = """Você é o tutor da Trilha de Estudos de matemática do Rafael (álgebra linear básica). Ele mandou as respostas abaixo para correção.

Corrija cada item: diga se está certo, explique o erro em até duas frases quando houver e dê a resposta certa. Não use ferramentas, faça as contas com cuidado.

Exercício:
{enunciado}

Resposta do Rafael:
{resposta}

Itens a corrigir:
{itens}

Termine com um bloco ```json exatamente neste formato, um objeto por item, na mesma ordem:
{{"itens": [{{"id": "...", "correto": true, "resposta_certa": ...}}]}}
"correto" diz se a resposta do Rafael está certa. "resposta_certa" segue o formato indicado em cada item."""


def montar_prompt(caso, formatos):
    linhas = [f"- {i['id']}: {i['descricao']} (formato de resposta_certa: {formatos[i['tipo']]})" for i in caso["itens"]]
    return PROMPT.format(enunciado=caso["enunciado"], resposta=caso["resposta"], itens="\n".join(linhas))


def extrair_json(texto):
    """Pega o último bloco ```json; sem bloco, o último objeto que começa com "itens"."""
    candidatos = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", texto, re.S)[::-1]
    for c in candidatos:
        try:
            return json.loads(c)
        except json.JSONDecodeError:
            continue
    inicio = texto.rfind('{"itens"')
    if inicio >= 0:
        try:
            return json.JSONDecoder().raw_decode(texto[inicio:])[0]
        except json.JSONDecodeError:
            pass
    return None


def numeros(valor):
    """Achata número, lista ou texto com números numa lista de floats."""
    if isinstance(valor, str):
        try:
            valor = json.loads(valor)
        except json.JSONDecodeError:
            return [float(x) for x in re.findall(r"-?\d+(?:[.,]\d+)?", valor.replace(",", "."))]
    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        return [float(valor)]
    if isinstance(valor, list):
        return [n for v in valor for n in numeros(v)]
    return []


def tamanho(valor):
    t = str(valor).lower().replace("×", "x").replace(" ", "").replace("ã", "a")
    if "naoexiste" in t or "inexist" in t or t in {"nao", "naodá", "naoda"}:
        return "nao existe"
    m = re.search(r"(\d+)x(\d+)", t)
    return f"{m.group(1)}x{m.group(2)}" if m else t


def resposta_bate(tipo, certa, dada):
    if tipo == "vf":
        return True
    if tipo == "tamanho":
        return tamanho(dada) == tamanho(certa)
    if tipo == "conjunto":
        return sorted(set(numeros(dada))) == sorted(set(numeros(certa)))
    return numeros(dada) == numeros(certa)


def corrigir(caso, saida):
    respostas = {str(i.get("id")): i for i in (saida or {}).get("itens", []) if isinstance(i, dict)}
    itens = []
    for g in caso["itens"]:
        r = respostas.get(g["id"])
        disse_certo = r.get("correto") if r else None
        if isinstance(disse_certo, str):
            disse_certo = disse_certo.strip().lower() in {"true", "sim", "certo", "verdadeiro"}
        julgou_bem = disse_certo is not None and disse_certo == g["aluno_certo"]
        certa_ok = None
        if not g["aluno_certo"] and r is not None:
            certa_ok = resposta_bate(g["tipo"], g["certa"], r.get("resposta_certa"))
        ok = julgou_bem and (g["aluno_certo"] or certa_ok)
        itens.append({
            "id": g["id"], "aluno_certo": g["aluno_certo"], "modelo_disse_certo": disse_certo,
            "resposta_modelo": r.get("resposta_certa") if r else None, "gabarito": g["certa"],
            "julgou_bem": julgou_bem, "resposta_certa_ok": certa_ok, "ok": bool(ok),
        })
    return itens


def rodar(modelo, caso, formatos, esforco):
    cmd = ["claude", "-p", montar_prompt(caso, formatos), "--model", modelo, "--output-format", "json",
           "--tools", "", "--no-session-persistence", "--setting-sources", "project", "--strict-mcp-config"]
    if esforco:
        cmd += ["--effort", esforco]
    with tempfile.TemporaryDirectory() as pasta:
        p = subprocess.run(cmd, cwd=pasta, capture_output=True, text=True, timeout=600)
    try:
        dados = json.loads(p.stdout)
    except json.JSONDecodeError:
        return {"caso": caso["id"], "erro": (p.stderr or p.stdout)[-500:]}
    texto = dados.get("result") or ""
    uso = dados.get("modelUsage") or {}
    return {
        "caso": caso["id"],
        "modelo_real": ", ".join(uso) or modelo,
        "custo_usd": dados.get("total_cost_usd", 0),
        "duracao_s": round(dados.get("duration_ms", 0) / 1000, 1),
        "tokens_saida": (dados.get("usage") or {}).get("output_tokens", 0),
        "texto": texto,
        "itens": corrigir(caso, extrair_json(texto)),
        "erro": dados.get("is_error") and texto,
    }


def resumir(execucoes):
    itens = [i for e in execucoes for i in e.get("itens", [])]
    errados = [i for i in itens if not i["aluno_certo"]]
    certos = [i for i in itens if i["aluno_certo"]]
    return {
        "itens_ok": sum(i["ok"] for i in itens), "itens": len(itens),
        "erros_pegos": sum(i["modelo_disse_certo"] is False for i in errados), "erros": len(errados),
        "resposta_certa_ok": sum(bool(i["resposta_certa_ok"]) for i in errados if i["modelo_disse_certo"] is False),
        "falsos_alarmes": sum(i["modelo_disse_certo"] is False for i in certos),
        "sem_resposta": sum(i["modelo_disse_certo"] is None for i in itens),
        "custo_usd": round(sum(e.get("custo_usd", 0) for e in execucoes), 4),
        "duracao_media_s": round(sum(e.get("duracao_s", 0) for e in execucoes) / max(len(execucoes), 1), 1),
        "falhas": sorted({e["caso"] for e in execucoes if e.get("erro")}),
    }


def registrar_linha(linha):
    if not os.path.exists(AVALIACAO):
        return False
    texto = open(AVALIACAO).read()
    if MARCA_FIM not in texto:
        return False
    open(AVALIACAO, "w").write(texto.replace(MARCA_FIM, linha + "\n" + MARCA_FIM))
    return True


def main():
    ap = argparse.ArgumentParser(description="Mesma prova de correção para cada modelo.")
    ap.add_argument("--modelos", default="opus,sonnet,haiku", help="separados por vírgula (aliases ou ids)")
    ap.add_argument("--casos", help="ids separados por vírgula, padrão todos")
    ap.add_argument("--rodadas", type=int, default=2, help="quantas vezes cada caso roda (as respostas variam)")
    ap.add_argument("--esforco", help="low, medium, high, xhigh ou max; padrão o do modelo")
    ap.add_argument("--paralelo", type=int, default=4)
    ap.add_argument("--nao-registrar", action="store_true", help="não escreve em avaliacao-modelos.md")
    args = ap.parse_args()

    base = json.load(open(CASOS))
    casos = base["casos"]
    if args.casos:
        quero = set(args.casos.split(","))
        casos = [c for c in casos if c["id"] in quero]
    modelos = [m.strip() for m in args.modelos.split(",") if m.strip()]
    os.makedirs(RESULTADOS, exist_ok=True)
    agora = datetime.datetime.now()

    for modelo in modelos:
        tarefas = [c for c in casos for _ in range(args.rodadas)]
        print(f"\n== {modelo}: {len(tarefas)} correções ({len(casos)} casos x {args.rodadas} rodadas)", flush=True)
        with concurrent.futures.ThreadPoolExecutor(args.paralelo) as ex:
            execucoes = list(ex.map(lambda c: rodar(modelo, c, base["formatos"], args.esforco), tarefas))
        r = resumir(execucoes)
        real = sorted({e.get("modelo_real", modelo) for e in execucoes if e.get("modelo_real")})
        nome = ", ".join(real) or modelo
        arquivo = os.path.join(RESULTADOS, f"{agora:%Y-%m-%d_%H%M}_{modelo}.json")
        json.dump({"data": agora.isoformat(timespec="minutes"), "modelo": nome, "esforco": args.esforco or "padrão",
                   "rodadas": args.rodadas, "resumo": r, "execucoes": execucoes},
                  open(arquivo, "w"), ensure_ascii=False, indent=1)

        print(f"   modelo: {nome}")
        print(f"   itens certos:     {r['itens_ok']}/{r['itens']}")
        print(f"   erros pegos:      {r['erros_pegos']}/{r['erros']} (com resposta certa: {r['resposta_certa_ok']})")
        print(f"   falsos alarmes:   {r['falsos_alarmes']}")
        if r["sem_resposta"] or r["falhas"]:
            print(f"   sem JSON/falhas:  {r['sem_resposta']} itens, casos {r['falhas']}")
        print(f"   custo: US$ {r['custo_usd']:.4f}   tempo médio por correção: {r['duracao_media_s']} s")
        perdidos = sorted({i["id"] for e in execucoes for i in e.get("itens", []) if not i["ok"]})
        if perdidos:
            print(f"   itens que falharam: {', '.join(perdidos)}")
        print(f"   detalhes: {os.path.relpath(arquivo, TRILHA)}")

        linha = (f"| {agora:%d/%m/%Y} | {nome} | {args.esforco or 'padrão'} | {args.rodadas} "
                 f"| {r['itens_ok']}/{r['itens']} | {r['erros_pegos']}/{r['erros']} | {r['resposta_certa_ok']}/{r['erros']} "
                 f"| {r['falsos_alarmes']} | {r['custo_usd']:.2f} | {r['duracao_media_s']} s |")
        if not args.nao_registrar and not registrar_linha(linha):
            print("   (não achei a tabela da bancada em avaliacao-modelos.md, linha não registrada)")


if __name__ == "__main__":
    sys.exit(main())
