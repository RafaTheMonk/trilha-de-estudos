#!/usr/bin/env python3
"""Fila de revisão espaçada da Trilha de Estudos.

Uso:
  python3 harness/revisar.py                       # itens vencidos hoje, até 5, intercalando assuntos
  python3 harness/revisar.py --max 3
  python3 harness/revisar.py --todos               # fila inteira, com a próxima data de cada item
  python3 harness/revisar.py --gabarito R02        # gabarito de um item, só depois da tentativa
  python3 harness/revisar.py --resultado R02 certo # ou errado; reagenda o item

Os itens ficam em revisoes.json, na raiz da trilha. Acerto faz o intervalo
subir na escada 1, 3, 7, 21, 60 dias. Erro volta para 1 dia. A listagem não
mostra o gabarito, para não estragar a tentativa.

Item novo entra editando revisoes.json, com gabarito conferido em Python:
  {"id": "R09", "nota": "matematica/.../NN-assunto.md", "enunciado": "...",
   "gabarito": "...", "intervalo": 1, "proxima": "AAAA-MM-DD", "historico": []}
"""

import argparse
import datetime
import json
import os
import sys

HARNESS = os.path.dirname(os.path.abspath(__file__))
TRILHA = os.path.dirname(HARNESS)
FILA = os.path.join(TRILHA, "revisoes.json")
ESCADA = [1, 3, 7, 21, 60]
CAMPOS = ("id", "nota", "enunciado", "gabarito", "intervalo", "proxima")


def carregar():
    if not os.path.exists(FILA):
        return []
    with open(FILA) as f:
        return json.load(f)


def salvar(itens):
    with open(FILA, "w") as f:
        json.dump(itens, f, ensure_ascii=False, indent=1)
        f.write("\n")


def validar(itens):
    problemas, ids = [], set()
    for i in itens:
        falta = [c for c in CAMPOS if c not in i]
        if falta:
            problemas.append(f"{i.get('id', '?')}: falta {', '.join(falta)}")
        if i.get("id") in ids:
            problemas.append(f"{i['id']}: id repetido")
        ids.add(i.get("id"))
        if "nota" in i and not os.path.exists(os.path.join(TRILHA, i["nota"])):
            problemas.append(f"{i.get('id', '?')}: nota {i['nota']} não existe")
    return problemas


def data(texto):
    return datetime.date.fromisoformat(texto)


def br(d):
    return d.strftime("%d/%m/%Y")


def assunto(item):
    return os.path.basename(item["nota"]).removesuffix(".md")


def intercalar(itens):
    """Mais atrasados primeiro, alternando entre notas para misturar assuntos."""
    grupos = {}
    for i in sorted(itens, key=lambda i: (i["proxima"], i["id"])):
        grupos.setdefault(i["nota"], []).append(i)
    fila = []
    while any(grupos.values()):
        for nota in grupos:
            if grupos[nota]:
                fila.append(grupos[nota].pop(0))
    return fila


def proximo_intervalo(atual, acertou):
    if not acertou:
        return ESCADA[0]
    return next((d for d in ESCADA if d > atual), ESCADA[-1])


def achar(itens, id_):
    for i in itens:
        if i["id"].lower() == id_.lower():
            return i
    sys.exit(f"Item {id_} não está em revisoes.json.")


def main():
    ap = argparse.ArgumentParser(description="Fila de revisão espaçada da trilha.")
    ap.add_argument("--max", type=int, default=5, help="quantos itens mostrar (padrão 5)")
    ap.add_argument("--todos", action="store_true", help="mostra a fila inteira")
    ap.add_argument("--gabarito", metavar="ID")
    ap.add_argument("--resultado", nargs=2, metavar=("ID", "certo|errado"))
    ap.add_argument("--hoje", type=data, default=datetime.date.today(), help=argparse.SUPPRESS)
    args = ap.parse_args()

    itens = carregar()
    for p in validar(itens):
        print("Aviso:", p)
    hoje = args.hoje

    if args.gabarito:
        i = achar(itens, args.gabarito)
        print(f"{i['id']} ({assunto(i)})\n\n{i['gabarito']}")
        return

    if args.resultado:
        id_, res = args.resultado
        if res not in ("certo", "errado"):
            sys.exit("O resultado é 'certo' ou 'errado'.")
        i = achar(itens, id_)
        acertou = res == "certo"
        i["intervalo"] = proximo_intervalo(i["intervalo"], acertou)
        i["proxima"] = (hoje + datetime.timedelta(days=i["intervalo"])).isoformat()
        i.setdefault("historico", []).append({"data": hoje.isoformat(), "acertou": acertou})
        salvar(itens)
        print(f"{i['id']}: {res}. Volta em {i['intervalo']} dia(s), em {br(data(i['proxima']))}.")
        return

    if args.todos:
        for i in sorted(itens, key=lambda i: (i["proxima"], i["id"])):
            acertos = sum(h["acertou"] for h in i.get("historico", []))
            print(f"{i['id']}  {br(data(i['proxima']))}  intervalo {i['intervalo']:2}  "
                  f"acertos {acertos}/{len(i.get('historico', []))}  {assunto(i)}")
        return

    vencidos = [i for i in itens if data(i["proxima"]) <= hoje]
    if not vencidos:
        futuros = sorted(itens, key=lambda i: i["proxima"])
        prox = f" Próximo: {futuros[0]['id']} em {br(data(futuros[0]['proxima']))}." if futuros else ""
        print(f"Nada para revisar hoje ({br(hoje)}).{prox}")
        return
    escolhidos = intercalar(vencidos)[:args.max]
    print(f"{len(escolhidos)} item(ns) para revisar hoje ({br(hoje)}), de {len(vencidos)} vencido(s).")
    print("Um de cada vez, sem consultar a nota.\n")
    for i in escolhidos:
        atraso = (hoje - data(i["proxima"])).days
        extra = f", {atraso} dia(s) de atraso" if atraso else ""
        print(f"{i['id']}  [{assunto(i)}]  intervalo {i['intervalo']} dia(s){extra}")
        print(f"{i['enunciado']}\n")


if __name__ == "__main__":
    sys.exit(main())
