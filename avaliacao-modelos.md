# Avaliação de modelos na trilha

Pergunta: dá para trocar o Opus por um modelo mais barato (Sonnet ou Haiku) nas sessões de estudo sem perder qualidade?

Começou em 05/11/2026. Até essa data todas as sessões foram no Opus 5.5, que serve de base para comparar.

## Como medir

São duas medidas que se completam:

| Medida | O que responde | Como roda |
|---|---|---|
| **Bancada** (prova fixa) | O modelo acha o erro do aluno sem inventar erro onde não tem? É o ponto fraco de modelo menor segundo as pesquisas. | `python3 harness/bancada.py` |
| **Sessões reais** | Quanto custa cada turno de estudo e se o processo da trilha foi seguido (conta conferida em Python, nota no formato, sem travessão). | `python3 harness/medir.py --registrar`, que roda sozinho no fim de cada sessão |

A bancada tem 7 casos e 20 itens, 9 deles com erro plantado. Os casos são tirados dos exercícios das notas 01 e 02 e ficam em `harness/casos.json`. Cada caso roda 2 vezes, porque a resposta do modelo varia de uma vez para outra. A bancada roda sem ferramentas, então o modelo não confere conta em Python. É um teste mais duro que a sessão real.

Para abrir a trilha com outro modelo, sempre de dentro da pasta, para o log cair no lugar certo:

```bash
cd ~/Desktop/TrilhaDeEstudos && claude --model sonnet
```

## Critério de decisão

O modelo novo vira o padrão da trilha se cumprir as três condições:

1. **Na bancada:** acertar pelo menos 36 de 40 itens (2 rodadas), deixar passar no máximo 1 erro a mais que o Opus e dar no máximo 1 falso alarme.
2. **Em 5 sessões reais:** checagens automáticas sem problema e "Python antes de salvar" sempre completo.
3. **Na sua impressão:** nenhuma correção errada do tutor e nota média de clareza 4 ou mais.

Se falhar só nas correções, a saída é usar o modelo novo para explicar e o Opus nas sessões em que você manda respostas para corrigir. Se falhar na clareza, volta para o Opus.

## Bancada

| Data | Modelo | Esforço | Rodadas | Itens certos | Erros pegos | Com resposta certa | Falsos alarmes | Custo (US$ API) | Tempo por correção |
|---|---|---|---|---|---|---|---|---|---|
| 05/11/2026 | claude-opus-5-5 | padrão | 2 | 40/40 | 18/18 | 18/18 | 0 | 0.47 | 5.9 s |
| 05/11/2026 | claude-sonnet-5-5 | padrão | 2 | 40/40 | 18/18 | 18/18 | 0 | 0.21 | 6.2 s |
| 05/11/2026 | claude-haiku-5-5 | padrão | 2 | 40/40 | 18/18 | 18/18 | 0 | 0.01 | 5.4 s |
<!-- bancada:fim -->

## Sessões reais

Gerado por `harness/medir.py`. Custo a preço de API, só para comparar, porque o plano cobra em limite de uso. Turnos de pesquisa e de manutenção do harness ficam fora do custo de estudo e aparecem na última coluna.

<!-- sessoes:inicio -->
| Data | Sessão | Modelo | Turnos de estudo | Custo do estudo (US$) | Por turno | Por turno a preço de Opus | Python antes de salvar | Outros turnos (US$) |
|---|---|---|---|---|---|---|---|---|
| 2026-11-03 | e24381d6 | Opus 5.5 | 3 | 0.46 | 0.15 | 0.15 | 0/0 | 1 (0.85) |
| 2026-11-05 | f8ddb23f | Opus 5.5 | 2 | 0.71 | 0.35 | 0.35 | 1/1 | 8 (7.38) |
| 2026-11-05 | cfadc69c | Sonnet 5.5 | 3 | 0.29 | 0.10 | 0.20 | 0/0 | 3 (3.79) |
<!-- sessoes:fim -->

### Checagens dos arquivos

<!-- checagens:inicio -->
Nenhum problema.
<!-- checagens:fim -->

## Sua impressão

Uma linha por sessão, preenchida no fim com o que você responder.

| Data | Sessão | Modelo | Clareza (1 a 5) | O tutor errou alguma correção ou conta? | Observação |
|---|---|---|---|---|---|

## Conclusão

Ainda em aberto.

**05/11/2026, bancada de base:** os três modelos acertaram 40 de 40 itens, pegaram os 18 erros plantados com a resposta certa e não deram nenhum falso alarme. A prova inteira custou US$ 0,47 no Opus, US$ 0,21 no Sonnet e US$ 0,015 no Haiku. Conferi as respostas do Haiku à mão e as explicações estão certas, inclusive um contraexemplo para (A·B)ᵗ ≠ Aᵗ·Bᵗ que ele montou sozinho.

Leitura: no nível das notas 01 e 02 a prova bate no teto e não separa os modelos. Corrigir esse conteúdo não é o gargalo, nem para o Haiku. A decisão fica com as sessões reais (seguir o processo e explicar com clareza). Quando a trilha chegar em determinante, inversa e sistemas, acrescentar casos mais difíceis à bancada e rodar de novo nos três.
