# 02 - Transposta e matriz simétrica

Estudado em 05/11/2026.

## Resumo

### Transposta

Transpor é trocar linhas por colunas: a 1ª linha vira a 1ª coluna, a 2ª linha vira a 2ª coluna, e assim por diante.

```
A = | 1  2  3 |        Aᵗ = | 1  4 |
    | 4  5  6 |             | 2  5 |
                            | 3  6 |
```

- Notação: `Aᵗ`, `Aᵀ` ou `A'` (lê-se "A linha" ou "A transposta").
- Tamanho: se A é m×n, Aᵗ é n×m.
- Elemento a elemento: `(Aᵗ)ᵢⱼ = aⱼᵢ`, os índices trocam de lugar.

### Matriz simétrica

A é simétrica quando `Aᵗ = A`. Só acontece em matriz **quadrada**, porque m×n só é igual a n×m se m = n.

Condição: `aᵢⱼ = aⱼᵢ` para todo i e j. A **diagonal principal é o espelho**: cada elemento fora dela tem que ser igual ao seu reflexo do outro lado.

```
| 1  7  3 |      7 com 7  (a12 = a21)
| 7  5  9 |      3 com 3  (a13 = a31)
| 3  9  2 |      9 com 9  (a23 = a32)
```

A diagonal (1, 5, 2) não tem par, pode ser qualquer valor.

Quantos pares conferir: 2×2 tem 1 par, 3×3 tem 3, n×n tem n·(n - 1)/2.

### Propriedades

| Propriedade | Vale? |
|---|---|
| (Aᵗ)ᵗ = A | sim, transpor duas vezes volta ao original |
| (A + B)ᵗ = Aᵗ + Bᵗ | sim |
| (k·A)ᵗ = k·Aᵗ | sim |
| (A·B)ᵗ = Bᵗ·Aᵗ | sim, **a ordem inverte** |

Conferindo a última com o exemplo da nota 01 (`A = | 1 2 ; 3 4 |`, `B = | 5 6 ; 7 8 |`):

```
(A·B)ᵗ = | 19  43 |      Bᵗ·Aᵗ = | 19  43 |      Aᵗ·Bᵗ = | 23  31 |
         | 22  50 |              | 22  50 |              | 34  46 |
```

Bᵗ·Aᵗ bate. Aᵗ·Bᵗ (sem inverter) não bate.

## Minhas perguntas

### Se A' = A numa matriz quadrada, os elementos espelhados são iguais? Exemplo com x = 1

Matriz da pergunta:

```
A = |   2     x² |
    | 2x - 1  0  |
```

**Sim, certo.** `A' = A` é a definição de simétrica, e isso obriga os elementos espelhados pela diagonal principal a serem iguais. Na 2×2 só tem um par: a12 com a21.

```
x² = 2x - 1
x² - 2x + 1 = 0
(x - 1)² = 0
x = 1
```

Δ = 0, então é raiz dupla: x = 1 é a **única** resposta. Conferindo:

```
A = | 2  1 |      Aᵗ = | 2  1 |      iguais
    | 1  0 |           | 1  0 |
```

**Ajuste de vocabulário:** não são as "extremidades", são os elementos **espelhados pela diagonal principal** (aᵢⱼ com aⱼᵢ). Na 2×2 coincide com os cantos fora da diagonal, mas numa 3×3 o a23 e o a32 ficam no meio das bordas e também precisam bater.

### Se A é simétrica, então A - A' = 0?

**Sim, certo.** Como `A' = A`, vale `A - A' = A - A`, e isso dá a **matriz nula** O (todos os elementos 0), não o número 0. A volta também vale: `A - A' = O` implica `A' = A`, então é um jeito de testar se A é simétrica.

Conferido em Python com uma 3×3 simétrica: `A - A.T` deu só zeros. Numa não simétrica (`[[1,2],[3,4]]`) deu `[[0,-1],[1,0]]`, diferente de O.

### Como confirmar que uma matriz é simétrica? E A + A', é simétrica?

Regra em 3 passos:

1. **É quadrada?** Se não for (ex: 2×3), nunca é simétrica, porque a transposta tem outro tamanho.
2. **Os pares espelhados batem?** Compare cada aᵢⱼ com aⱼᵢ, só de um lado da diagonal. São n·(n - 1)/2 pares. Basta um par diferente para não ser simétrica.
3. **A diagonal principal não entra no teste**, ela se espelha em si mesma.

Se a matriz tiver incógnita, iguala cada par e resolve, como no x² = 2x - 1 acima.

**A + A' é sempre simétrica**, para qualquer A quadrada, simétrica ou não:

```
(A + A')' = A' + (A')' = A' + A = A + A'
```

Exemplo: `B = | 1 2 ; 3 4 |` dá `B + B' = | 2 5 ; 5 8 |`. O mesmo vale para A·A', usando (A·B)ᵗ = Bᵗ·Aᵗ: `(A·A')' = (A')'·A' = A·A'`. Conferido em Python com 1000 matrizes 4×4 aleatórias.

## Em código

```python
def transposta(A):
    return [list(coluna) for coluna in zip(*A)]

def eh_simetrica(A):
    return A == transposta(A)
```

No NumPy: `A.T` dá a transposta e `(A == A.T).all()` testa se é simétrica.

## Exercícios

**1.** Escreva a transposta e diga o tamanho:

```
A = | 1  4  7 |
    | 2  5  8 |
```

**2.** Ache x e y para a matriz ser simétrica:

```
| 1  x+y  3 |
| 5   2   y |
| 3   4   0 |
```

**3.** Ache x para a matriz ser simétrica. Quantas respostas existem?

```
| 3  x² |
| 9  1  |
```

**4.** Essa matriz é simétrica? Por quê?

```
| 1  2  3 |
| 2  4  5 |
| 3  6  6 |
```

<details>
<summary>Gabarito (tente antes de abrir)</summary>

**1.** 3×2:

```
Aᵗ = | 1  2 |
     | 4  5 |
     | 7  8 |
```

**2.** a23 = a32 dá y = 4. a12 = a21 dá x + y = 5, então x = 1. O par a13 = a31 já bate (3 = 3).

**3.** x² = 9, então x = 3 **ou** x = -3. Duas respostas, diferente da pergunta original, que tinha raiz dupla.

**4.** Não. a23 = 5 e a32 = 6. Os outros pares batem (2 com 2, 3 com 3), mas basta um par diferente para não ser simétrica.

</details>
