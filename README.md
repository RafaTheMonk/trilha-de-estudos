# Trilha de Estudos

Tutor de matemática que roda no Claude Code em cima de uma pasta de Markdown, e um harness em Python que mede, com dados, se um modelo mais barato dá conta do mesmo trabalho.

O conteúdo começou em álgebra linear (multiplicação de matrizes, transposta e matriz simétrica) e cresce a cada sessão de estudo.

## Como o tutor funciona

O protocolo está no [`CLAUDE.md`](CLAUDE.md), que o Claude Code lê no começo de cada sessão:

- Cada assunto vira uma nota numerada em `area/subarea/NN-assunto.md`, com resumo, exemplos, as dúvidas reais feitas na conversa e exercícios com gabarito escondido em `<details>`.
- O [`progresso.md`](progresso.md) guarda o mapa de assuntos, os próximos passos e uma linha do tempo com as perguntas, os acertos e os erros de cada sessão.
- O status de cada assunto (visto, praticando, dominado) só sobe com evidência: exercício resolvido sozinho e certo.
- Toda conta de exemplo e de gabarito é conferida em Python antes de ser salva.

O desenho segue o que a literatura recente aponta como decisivo. Em Bastani et al. (PNAS, 2025), com cerca de mil alunos de matemática do ensino médio, o GPT-4 usado como chat livre reduziu em 17% a nota na prova sem IA. A versão com guardrails (dicas graduais, gabarito e erros comuns no prompt) não teve esse prejuízo. Os ensaios randomizados de Kestin et al. (Scientific Reports, 2025; N = 194, física em Harvard) e De Simone et al. (Banco Mundial, 2025; +0,31 desvio-padrão em seis semanas na Nigéria) mostraram ganho com tutoria estruturada usando GPT-4, um modelo de 2023. O protocolo pesa mais que a potência bruta do modelo.

## A pergunta: dá para usar um modelo mais barato?

Medindo os logs das sessões, cerca de 90% dos tokens são contexto relido do cache (1,1 milhão de 1,27 milhão) e a saída gerada é só uns 1%. Por isso o Sonnet 5.5 corta de 35% a 45% do custo por turno em relação ao Opus 5.5, e não 50%: a leitura de cache custa o mesmo US$ 0,20 por milhão de tokens nos dois. O Haiku 5.5 sai por volta de 1/30.

O risco não está em explicar, está em corrigir o aluno. O MathTutorBench (Macina et al., EMNLP 2025) mostra que saber resolver não se traduz em saber ensinar, e que a tutoria piora em diálogos longos. "LLMs cannot spot math errors" (2025) mostra que mesmo modelos de ponta têm dificuldade para localizar o primeiro passo errado numa solução de estudante.

## O harness

| Script | O que faz |
|---|---|
| [`harness/medir.py`](harness/medir.py) | Lê os logs JSONL do Claude Code, separa a sessão em turnos, tira do custo de estudo os turnos de pesquisa na web, subagentes e manutenção do harness e calcula o custo por modelo, contando gravação de cache com TTL de 1 hora (2x a entrada) e a faixa do Haiku acima de 100 mil tokens (5x). Também confere se houve verificação em Python antes de cada nota salva e se os arquivos seguem o formato. Guarda tudo em `harness/sessoes.json`, porque os logs somem depois de 30 dias. |
| [`harness/bancada.py`](harness/bancada.py) | Aplica a mesma prova de correção a cada modelo: 7 casos e 20 itens, 9 com erro plantado (erro de sinal, produto elemento a elemento no lugar de linha por coluna, raiz esquecida, propriedade da transposta invertida), com gabaritos conferidos em Python ([`casos.json`](harness/casos.json)). Cada caso roda em `claude -p` isolado, sem ferramentas, sem MCP e sem salvar sessão, em duas rodadas, com saída JSON por item e nota automática. |

O critério de decisão está em [`avaliacao-modelos.md`](avaliacao-modelos.md). O modelo mais barato vira o padrão se cumprir três condições:

- acertar pelo menos 36 de 40 itens na bancada, deixar passar no máximo um erro a mais que o Opus e dar no máximo um falso alarme;
- passar por cinco sessões reais com as checagens limpas;
- ter avaliação média de clareza de 4 ou mais, sem erro de correção.

Se falhar só na correção, a saída é híbrida: o modelo barato explica e o Opus corrige.

## Resultado de base (05/11/2026)

| Modelo | Itens certos | Erros pegos | Falsos alarmes | Custo da prova (US$, preço de API) |
|---|---|---|---|---|
| Opus 5.5 | 40/40 | 18/18 | 0 | 0,47 |
| Sonnet 5.5 | 40/40 | 18/18 | 0 | 0,21 |
| Haiku 5.5 | 40/40 | 18/18 | 0 | 0,015 |

No nível atual do conteúdo a prova bate no teto: corrigir esse material não separa os modelos, nem para o Haiku. A decisão passa a depender das sessões reais e de casos mais difíceis conforme a trilha avança (determinante, inversa, sistemas). O andamento fica em [`avaliacao-modelos.md`](avaliacao-modelos.md).

## Estrutura

```
trilha-de-estudos/
├── CLAUDE.md               protocolo do tutor
├── progresso.md            mapa de assuntos, próximos passos e linha do tempo
├── avaliacao-modelos.md    critério e resultados da comparação de modelos
├── harness/
│   ├── medir.py            custo e checagens das sessões reais, por modelo
│   ├── bancada.py          mesma prova de correção para cada modelo, nota automática
│   ├── casos.json          casos da prova com gabarito
│   ├── sessoes.json        histórico das sessões (os logs somem em 30 dias)
│   └── resultados/         saída completa de cada rodada da bancada
└── matematica/
    └── algebra-linear/
        ├── 01-multiplicacao-de-matrizes.md
        └── 02-transposta-e-matriz-simetrica.md
```

## Como usar

Requer o [Claude Code](https://code.claude.com) logado e Python 3.10 ou mais novo. Os scripts usam só a biblioteca padrão.

```bash
cd trilha-de-estudos
claude --model sonnet                          # estudar com o modelo escolhido

python3 harness/medir.py --registrar           # custo e checagens das sessões
python3 harness/bancada.py                     # prova nos três modelos, 2 rodadas
python3 harness/bancada.py --modelos haiku --rodadas 1 --casos C1,C7
```

A bancada gasta do limite do plano. A prova inteira custou o equivalente a US$ 0,47 no Opus e menos de US$ 0,02 no Haiku.

## Pesquisas citadas

- Bastani et al. (2025). [Generative AI without guardrails can harm learning: Evidence from high school mathematics](https://papers.ssrn.com/abstract=4895486). PNAS 122(26).
- Kestin et al. (2025). AI tutoring outperforms in-class active learning. Scientific Reports, [doi:10.1038/s41598-025-97652-6](https://doi.org/10.1038/s41598-025-97652-6).
- De Simone et al. (2025). [From Chalkboards to Chatbots: Evaluating the Impact of Generative AI on Learning Outcomes in Nigeria](https://econpapers.repec.org/RePEc:wbk:wbrwps:11125). World Bank Policy Research Working Paper 11125.
- Macina et al. (2025). [MathTutorBench: A Benchmark for Measuring Open-ended Pedagogical Capabilities of LLM Tutors](https://arxiv.org/abs/2502.18940). EMNLP 2025.
- [LLMs cannot spot math errors, even when allowed to peek into the solution](https://arxiv.org/abs/2509.01395) (2025).
- [Artificial Analysis Intelligence Index](https://artificialanalysis.ai) (Opus 5.5: 58, Sonnet 5.5: 56, Haiku 5.5: 43).
- [Claude Code, configuração de modelo](https://code.claude.com/docs/en/model-config).
