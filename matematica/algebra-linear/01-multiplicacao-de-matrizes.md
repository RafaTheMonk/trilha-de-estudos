# 01 - Multiplicação de matrizes

Estudado em 03 e 04/11/2026.

## Resumo

Cada elemento do resultado sai de uma **linha da primeira** matriz com uma **coluna da segunda**: multiplica os pares e soma tudo.

### Condição

O número de colunas de A precisa ser igual ao número de linhas de B.

```
A (m × n)  ·  B (n × p)  =  C (m × p)
      └──┬──┘
    os do meio precisam ser iguais
```

**Macete:** escreva os tamanhos lado a lado. Os do meio precisam ser iguais e somem. Os de fora dão o tamanho do resultado.

### Fórmula

```
c_ij = a_i1·b_1j + a_i2·b_2j + ... + a_in·b_nj
```

Linha `i` de A com coluna `j` de B.

## Exemplo 2×2 · 2×2

```
A = | 1  2 |      B = | 5  6 |
    | 3  4 |          | 7  8 |
```

| Posição | Conta | Resultado |
|---|---|---|
| c11 | 1·5 + 2·7 | 19 |
| c12 | 1·6 + 2·8 | 22 |
| c21 | 3·5 + 4·7 | 43 |
| c22 | 3·6 + 4·8 | 50 |

```
A · B = | 19  22 |      B · A = | 23  34 |
        | 43  50 |              | 31  46 |
```

A·B deu diferente de B·A, porque **a ordem importa**.

## Propriedades

| Propriedade | Vale? |
|---|---|
| Comutativa (A·B = B·A) | não, em geral |
| Associativa ((A·B)·C = A·(B·C)) | sim |
| Distributiva (A·(B + C) = A·B + A·C) | sim |
| Identidade (A·I = I·A = A) | sim |

**Por que é assim:** cada matriz é uma transformação (girar, esticar, projetar). A·B equivale a aplicar B primeiro e depois A.

## Minhas perguntas

### Dá para multiplicar duas matrizes 2×3?

**Não.** `2×3 · 2×3`: os do meio são 3 e 2, e não batem.

O que dá para fazer com elas:

| Operação | Tamanhos | Funciona? |
|---|---|---|
| A · B | 2×3 · 2×3 | não |
| A · Bᵀ (transposta de B) | 2×3 · 3×2 → 2×2 | sim |
| Aᵀ · B | 3×2 · 2×3 → 3×3 | sim |
| Elemento a elemento (Hadamard) | 2×3 e 2×3 → 2×3 | sim, mas é outra operação |

Exemplo com `A = | 1 2 3 ; 4 5 6 |` e `B = | 1 0 2 ; 3 1 1 |`:

```
A · Bᵀ = |  7   8 |      Elemento a elemento = |  1  0  6 |
         | 16  23 |                            | 12  5  6 |
```

Transpor é virar linhas em colunas. No NumPy, `A * B` multiplica elemento a elemento e `A @ B` faz a multiplicação de matrizes.

### E 2×3 vezes 3×1?

**Sim.** `2×3 · 3×1` dá **2×1**.

```
| 1  2  3 |   | 2 |   | 1·2 + 2·1 + 3·3 |   | 13 |
| 4  5  6 | · | 1 | = | 4·2 + 5·1 + 6·3 | = | 31 |
              | 3 |
```

Ao contrário (3×1 · 2×3) não dá, porque 1 ≠ 2.

Esse é o caso **matriz vezes vetor**, que é como se escreve um sistema de equações:

```
| 1  2  3 |   | x |   | 13 |        x + 2y + 3z = 13
| 4  5  6 | · | y | = | 31 |   →   4x + 5y + 6z = 31
              | z |
```

## Em código

```python
def multiplicar(A, B):
    m, n, p = len(A), len(B), len(B[0])
    assert len(A[0]) == n, "colunas de A != linhas de B"
    C = [[0] * p for _ in range(m)]
    for i in range(m):          # linha de A
        for j in range(p):      # coluna de B
            for k in range(n):  # percorre o par
                C[i][j] += A[i][k] * B[k][j]
    return C
```

## Exercícios

**1.** Diga se a multiplicação existe e, se existir, o tamanho do resultado:

- a) 3×2 · 2×4
- b) 4×1 · 4×1
- c) 1×3 · 3×1
- d) 2×2 · 3×2

**2.** Calcule:

```
| 2  1 |   | 1 |
| 0  3 | · | 4 |
```

**3.** Calcule:

```
             | 3 |
| 1  0  2 | · | 1 |
             | 2 |
```

**4.** Com `A = | 1 2 ; 0 1 |` e `B = | 3 0 ; 1 2 |`, calcule A·B e B·A. Deram iguais?

<details>
<summary>Gabarito (tente antes de abrir)</summary>

**1.** a) existe, 3×4. b) não existe (1 ≠ 4). c) existe, 1×1 (um número só). d) não existe (2 ≠ 3).

**2.**

```
| 2·1 + 1·4 |   |  6 |
| 0·1 + 3·4 | = | 12 |
```

**3.** `1·3 + 0·1 + 2·2 = 7`, resultado `| 7 |` (matriz 1×1).

**4.**

```
A · B = | 5  4 |      B · A = | 3  6 |
        | 1  2 |              | 1  4 |
```

Não deram iguais. Mais um caso em que a ordem muda o resultado.

</details>
