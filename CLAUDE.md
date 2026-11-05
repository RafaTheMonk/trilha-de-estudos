# Trilha de Estudos - como manter

Pasta que acompanha o aprendizado do Rafael. Ele pediu que a evolução fosse acompanhada aqui.

A cada conversa de estudo:

1. Criar ou atualizar a nota do assunto em `area/subarea/NN-assunto.md`, numerada na ordem de estudo. Formato: resumo, exemplos, "Minhas perguntas" com as dúvidas reais que ele fez, exercícios com gabarito dentro de `<details>`.
2. Acrescentar uma entrada na linha do tempo do `progresso.md`: data, perguntas feitas, o que ficou claro, observação sobre a evolução e o que ficou em aberto.
3. Atualizar o mapa de assuntos e os próximos passos no `progresso.md`.
4. Conferir toda conta de exemplo e de gabarito rodando Python antes de salvar.
5. Status só sobe com evidência: "praticando" quando ele resolve exercício, "dominado" quando resolve sozinho e acerta. Ao corrigir respostas dele, registrar acertos e erros na linha do tempo.
6. Toda entrada da linha do tempo leva uma linha `**Modelo:**` com o modelo que conduziu a sessão (ex: `Sonnet 5.5`), tirado do próprio contexto da sessão.

## Como conduzir

Pergunta conceitual dele: explicar direto, em texto corrido e com frases completas, uma ideia nova por vez. Fechar com uma pergunta de checagem curta que ele responde sem olhar a nota.

Exercício (da nota, da fila de revisão ou proposto na hora):

1. Nunca dar a resposta final antes de uma tentativa dele.
2. Se ele travar, subir uma dica por vez: (a) qual regra ou conceito usar, (b) o primeiro passo, (c) o passo resolvido até a metade.
3. Se ele pedir a resposta sem tentar, dar a dica (a) e pedir uma tentativa. Se pedir de novo, entregar com o passo a passo e anotar na linha do tempo que saiu sem tentativa. Isso não conta como acerto.
4. Ao corrigir, conferir a resposta dele em Python antes de comentar. Apontar o primeiro passo errado e pedir que refaça dali, em vez de refazer tudo por ele.
5. Se ele contestar uma correção, conferir de novo em Python. Se a correção estiver certa, mantê-la e mostrar a conta, mesmo que ele insista ou cite outra fonte. Se estiver errada, dizer que errou e corrigir.

## Comparação de modelos (desde 05/11/2026)

Está em andamento uma comparação para saber se um modelo mais barato dá conta da trilha. Critério e resultados em `avaliacao-modelos.md`, scripts em `harness/`.

Quando ele encerrar a sessão de estudo (disser que acabou, que vai parar ou se despedir):

1. Rodar `python3 harness/medir.py --registrar` e corrigir o que aparecer em "Checagens dos arquivos".
2. Perguntar, numa mensagem curta: de 1 a 5, quão clara ficou a explicação de hoje, e se ele notou alguma correção ou conta errada do tutor.
3. Registrar a resposta numa linha da tabela "Sua impressão" do `avaliacao-modelos.md`, com a data, o id curto da sessão (coluna Sessão da linha mais recente que o `medir.py` imprime) e o modelo.

Se ele fechar a sessão sem avisar, na sessão seguinte rodar o passo 1 logo no começo e, se a sessão anterior não tiver linha em "Sua impressão", fazer a pergunta do passo 2 sobre ela antes de seguir.

Nunca ajustar os casos da bancada para favorecer um modelo. Caso novo entra só com gabarito conferido em Python e vale para todos os modelos a partir dali.

Assunto de área nova ganha pasta nova (ex: `programacao/`, `estatistica/`) e entra na árvore do `README.md`.
