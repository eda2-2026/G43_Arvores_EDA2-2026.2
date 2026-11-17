# Lanchonete em Árvores

Trabalho de **Estruturas de Dados 2** sobre árvores binárias de busca: **BST**, **AVL** e **Rubro-Negra** aplicadas aos pedidos de uma lanchonete.

## Cenário

Cada pedido recebe um **número sequencial** no caixa (1, 2, 3...), e esse número é a chave da árvore.

Escolhemos esse contexto porque os pedidos chegam **em ordem crescente**. Chaves chegando ordenadas são o pior caso da BST: cada número novo é maior que todos os anteriores, vai sempre para a direita, e a árvore vira uma lista encadeada. É exatamente esse problema que as árvores balanceadas resolvem.

| Na lanchonete | Na árvore |
|---|---|
| Consultar o pedido #152 | busca |
| Novo pedido no caixa | inserção |
| Pedido entregue ou cancelado | remoção |
| Próximo pedido a preparar (o mais antigo) | mínimo |
| Pedido que vem depois do #152 | sucessor |
| Pedidos do #100 ao #150 | busca por intervalo |

## Base de dados

[`dados/pedidos.csv`](dados/pedidos.csv): **2.186 pedidos simulados** de uma semana (16/11 a 22/11/2026), com a lanchonete aberta das 11:00 às 23:00. Os números são sequenciais e acompanham o horário. Cada pedido tem de 1 a 4 itens do cardápio, e o valor é a soma dos itens. 165 pedidos terminaram cancelados.

Campos: `numero, data_hora, cliente, itens, valor, status`.

A base é gerada por [`dados/gerar_base.py`](dados/gerar_base.py) com semente 42: rodar de novo gera o mesmo arquivo (um teste confere isso).

## Estrutura

```
├── dados/
│   ├── gerar_base.py      # gerador da base (semente 42)
│   └── pedidos.csv
├── src/
│   ├── pedidos.py         # Pedido, cardápio e leitura do CSV
│   └── arvores/
│       ├── base.py        # comum a todas: busca, mínimo, sucessor, intervalo, altura, desenho
│       ├── bst.py         # BST sem balanceamento
│       └── avl.py         # AVL
└── tests/
    ├── test_arvores.py    # operações comuns, rodam em todas as árvores
    ├── test_avl.py        # casos de rotação, fator e altura da AVL
    └── test_pedidos.py    # base de dados e gerador
```

## Como rodar

Python 3.10 ou mais novo, sem bibliotecas externas. Todos os comandos na raiz do projeto:

```bash
python -m unittest -v        # testes
python -m dados.gerar_base   # gera dados/pedidos.csv de novo (opcional)
```

## Parte comum

[`src/arvores/base.py`](src/arvores/base.py) concentra tudo o que só **consulta** a árvore e é igual em qualquer árvore binária de busca: buscar, mínimo, máximo, sucessor, intervalo, percurso em ordem, altura e desenho no terminal. Cada árvore implementa só o que muda: inserir, remover e validar as próprias regras.

Os métodos são **iterativos**: com os pedidos em ordem, a BST chega a milhares de níveis, e uma recursão dessa profundidade estoura o limite do Python.

O desenho mostra a árvore deitada, com a raiz à esquerda, o filho direito acima e o esquerdo abaixo:

```
    ┌── #7
┌── #6
│   └── #5
#4
│   ┌── #3
└── #2
    └── #1
```

## BST

[`src/arvores/bst.py`](src/arvores/bst.py) · **Regra:** menores à esquerda, maiores à direita. Busca, inserção e remoção custam O(h), onde h é a altura.

A BST nunca se reorganiza: a altura depende só da ordem de chegada. Com a base real na ordem do arquivo, a altura é **2.186**, igual ao número de pedidos. Para achar o pedido #k são k comparações, então a média é (n + 1) / 2.

Remoção: a folha sai; o nó com um filho é trocado pelo filho; o nó com dois filhos recebe o sucessor (o menor da subárvore direita), e quem sai é o sucessor.

## AVL

[`src/arvores/avl.py`](src/arvores/avl.py) · **Regra:** em todo nó, o fator `altura(esquerda) - altura(direita)` fica entre -1 e +1. Isso limita a altura a cerca de 1,44 · log2(n), então busca, inserção e remoção custam O(log n).

Depois de inserir ou remover, cada nó do caminho recalcula a própria altura. Se o fator chegar a +2 ou -2, a árvore rotaciona:

| Caso | Fator do nó | Fator do filho | Correção |
|---|:-:|:-:|---|
| esquerda-esquerda | +2 | ≥ 0 | rotação à direita |
| esquerda-direita | +2 | < 0 | rotação à esquerda no filho, depois à direita |
| direita-direita | -2 | ≤ 0 | rotação à esquerda |
| direita-esquerda | -2 | > 0 | rotação à direita no filho, depois à esquerda |

O filho com fator 0 só aparece na **remoção**; na inserção ele sempre pende para um dos lados.

Na inserção, uma correção (1 ou 2 rotações) no nó desequilibrado mais baixo já basta, porque a subárvore volta à altura que tinha antes. Na remoção, corrigir um nó pode diminuir a altura da subárvore e desequilibrar o de cima, então a correção pode subir até a raiz.

Com os pedidos chegando em ordem, cai sempre no caso **direita-direita**. Com `AVL(verbose=True)` a árvore imprime cada caso e cada rotação, e o desenho mostra o fator de cada nó:

```
  inserir 1
  inserir 2
  inserir 3
    [AVL] caso direita-direita em #1 (fator -2)
    [AVL] rotação à esquerda em #1 (#2 sobe)
  inserir 4
  inserir 5
    [AVL] caso direita-direita em #3 (fator -2)
    [AVL] rotação à esquerda em #3 (#4 sobe)
  inserir 6
    [AVL] caso direita-direita em #2 (fator -2)
    [AVL] rotação à esquerda em #2 (#4 sobe)
  inserir 7
    [AVL] caso direita-direita em #5 (fator -2)
    [AVL] rotação à esquerda em #5 (#6 sobe)

    ┌── #7 [f=+0]
┌── #6 [f=+0]
│   └── #5 [f=+0]
#4 [f=+0]
│   ┌── #3 [f=+0]
└── #2 [f=+0]
    └── #1 [f=+0]
```

Os mesmos 7 pedidos que deixam a BST com 7 níveis ficam com 3 na AVL. Com números em ordem, a AVL termina sempre com a **menor altura possível**, ⌊log2 n⌋ + 1: a base real inteira (2.186 pedidos) cabe em **12 níveis**, contra 2.186 na BST.

## Testes

Depois das operações, `validar()` confere as regras da árvore, e o conteúdo é comparado com um dicionário comum, que serve de resultado esperado.

- **Todas as árvores** ([`test_arvores.py`](tests/test_arvores.py)): árvore vazia, número repetido, remoção de folha, nó com um filho e nó com dois filhos, 3.000 inserções e remoções misturadas, sucessor e intervalo. Aqui `validar()` confere a ordem das chaves e o tamanho.
- **AVL** ([`test_avl.py`](tests/test_avl.py)): um teste para cada um dos 4 casos de rotação, o caso de filho equilibrado na remoção, no máximo 2 rotações por inserção, altura dentro do limite teórico e mínima com números em ordem. Aqui `validar()` também confere a altura guardada e o fator de cada nó; um teste monta uma árvore desequilibrada à mão para garantir que a validação acusa o erro.

## Integrantes

| Matrícula | Nome |
|---|---|
| 231011097 | André Meyer |
