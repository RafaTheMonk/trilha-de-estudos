# Progresso

## Mapa de assuntos

| Área | Assunto | Status | Nota |
|---|---|---|---|
| Álgebra linear | Multiplicação de matrizes | visto | [01](matematica/algebra-linear/01-multiplicacao-de-matrizes.md) |
| Álgebra linear | Transposta e matriz simétrica | praticando | [02](matematica/algebra-linear/02-transposta-e-matriz-simetrica.md) |

**Status:** visto (explicado e entendido) → praticando (resolvendo exercícios) → dominado (resolve sozinho, sem consultar).

## Próximos passos sugeridos

1. Resolver os exercícios da nota 01 sem olhar o gabarito (ainda pendentes).
2. Resolver os exercícios da nota 02.
3. Matriz identidade.
4. Sistemas lineares na forma A·x = b.
5. Determinante.
6. Matriz inversa.

## Linha do tempo

### 05/11/2026 (2ª sessão) - Transposta e matriz simétrica

**Perguntas feitas:**

1. Se A é simétrica, então A - A' = 0.
2. Se há uma regra para confirmar que uma matriz é simétrica (e pediu para ver A + A').

**Modelo:** Sonnet 5.5

**O que ficou claro:**

- A' = A implica A - A' = matriz nula. A volta também vale.
- Ajuste: o resultado é a matriz nula O, não o número 0.
- Regra: quadrada, pares espelhados iguais, diagonal livre. A + A' e A·A' são sempre simétricas.

**Observação:** montou sozinho uma consequência da definição de simétrica, sem exemplo numérico. Ainda não é exercício resolvido, o status continua "praticando".

**Em aberto:** exercícios das notas 01 e 02, e os dois propostos no fim da sessão (transposta de `| 1 2 3 ; 2 4 5 |` e x em `| 1 x ; 4 1 |`).

### 05/11/2026 - Transposta e matriz simétrica

**Perguntas feitas:**

1. Se `A' = A` numa matriz quadrada quer dizer que os elementos "das extremidades" são iguais, com o exemplo `| 2  x² ; 2x-1  0 |` e a resposta x = 1.

**Modelo:** Opus 5.5

**O que ficou claro:**

- `A' = A` é a definição de matriz simétrica: aᵢⱼ = aⱼᵢ, espelho pela diagonal principal.
- Resolveu sozinho o exemplo: igualou x² = 2x - 1 e chegou em x = 1. **Acerto.** (Raiz dupla, então é a única resposta.)
- Ajuste: o certo é "espelhados pela diagonal", não "extremidades". Na 2×2 dá no mesmo, na 3×3 não.
- Visto junto: (A·B)ᵗ = Bᵗ·Aᵗ, ligando com a nota 01.

**Observação:** pulou os exercícios da nota 01 e chegou com uma questão de prova já montada, aplicando a definição de simétrica sem ajuda. Foi o primeiro exercício resolvido sozinho na trilha, por isso o assunto entra como "praticando".

**Em aberto:** exercícios da nota 01 e da nota 02. O exercício 3 da nota 02 testa o caso com duas respostas (x² = 9), contraste com a raiz dupla da pergunta.

### 03 e 04/11/2026 - Multiplicação de matrizes

**Perguntas feitas:**

1. Como funciona a multiplicação de matrizes.
2. Se dá para multiplicar duas matrizes 2×3.
3. Se dá para multiplicar uma 2×3 por uma 3×1.

**Modelo:** Opus 5.5

**O que ficou claro:**

- Regra linha × coluna: multiplica par a par e soma.
- Condição: colunas da primeira = linhas da segunda. Os números de fora dão o tamanho do resultado.
- A ordem importa, A·B costuma ser diferente de B·A.
- Apareceram de passagem: transposta, produto elemento a elemento e matriz vezes vetor como sistema de equações.

**Observação:** a 2ª e a 3ª perguntas já testam a condição de tamanhos em casos novos, um caso que não dá e outro que dá. É o passo natural depois da explicação geral.

**Em aberto:** ainda sem exercício resolvido sozinho. Os 4 exercícios da nota 01 servem para isso.
