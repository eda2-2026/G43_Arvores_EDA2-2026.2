# Lanchonete em Árvores

Trabalho de **Estruturas de Dados 2** sobre árvores binárias de busca: **BST**, **AVL** e **Rubro-Negra** aplicadas aos pedidos de uma lanchonete.

## Cenário

Cada pedido recebe um **número sequencial** no caixa (1, 2, 3...), e esse número é a chave da árvore. A árvore é o **registro de pedidos**: cresce a semana inteira e é consultada o tempo todo.

Escolhemos esse contexto porque os pedidos chegam **em ordem crescente**. Chaves chegando ordenadas são o pior caso da BST: cada número novo é maior que todos os anteriores, vai sempre para a direita, e a árvore vira uma lista encadeada. É exatamente esse problema que as árvores balanceadas resolvem.

| Na lanchonete | Na árvore |
|---|---|
| Consultar o pedido #152 | busca |
| Novo pedido no caixa | inserção |
| Cancelar um pedido | remoção |
| Próximo pedido a preparar | sucessor do último entregue |
| Pedido registrado depois do #152 | sucessor |
| Painel da cozinha; fechamento de caixa do #1 ao #331 | busca por intervalo |

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
│   ├── lanchonete.py      # regras da lanchonete, sobre qualquer uma das árvores
│   └── arvores/
│       ├── base.py        # comum a todas: busca, mínimo, sucessor, intervalo, altura, desenho
│       ├── bst.py         # BST sem balanceamento
│       ├── avl.py         # AVL
│       └── rubro_negra.py # Rubro-Negra
└── tests/
    ├── test_arvores.py    # operações comuns, rodam em todas as árvores
    ├── test_avl.py        # casos de rotação, fator e altura da AVL
    ├── test_rubro_negra.py # casos de inserção e remoção, regras e altura da Rubro-Negra
    ├── test_lanchonete.py # regras da lanchonete nas três árvores e a demonstração
    └── test_pedidos.py    # base de dados e gerador
├── main.py                # demonstração passo a passo
```

## Como rodar

Python 3.10 ou mais novo, sem bibliotecas externas. Todos os comandos na raiz do projeto:

```bash
python main.py               # demonstração (python main.py 3 roda só a parte 3)
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

## Rubro-Negra

[`src/arvores/rubro_negra.py`](src/arvores/rubro_negra.py) · **Regras** (Cormen, cap. 13):

1. todo nó é vermelho ou preto;
2. a raiz é preta;
3. toda folha vazia é preta;
4. nó vermelho não tem filho vermelho;
5. todo caminho de um nó até as folhas vazias passa pela mesma quantidade de nós pretos (a *altura preta*).

Juntas, elas limitam a altura a 2 · log2(n + 1). As regras são mais folgadas que as da AVL: a árvore fica um pouco mais alta, mas se rebalanceia com menos rotações, trocando cores (*recolorações*).

Todas as folhas vazias e o pai da raiz são **o mesmo nó sentinela preto**. Assim todo nó tem pai e filhos de verdade, com cor, e o código não precisa testar "está vazio?" a cada passo.

**Inserção.** O nó novo entra vermelho, então a única regra que pode quebrar é a 4 (pai vermelho). Quem decide o caso é o **tio**:

| Caso | Situação | Correção |
|---|---|---|
| 1 | tio vermelho | recolore pai, tio e avô; o problema sobe para o avô |
| 2 | tio preto, nó em "joelho" (filho direito de um filho esquerdo, ou o espelho) | rotação no pai; vira o caso 3 |
| 3 | tio preto, nó em linha reta | recolore e rotação no avô; fim |

No máximo 2 rotações por inserção.

**Remoção.** Se o nó que sai é preto, um caminho fica com um preto a menos: o *duplo preto*. Quem decide o caso é o **irmão** do nó que ficou com o duplo preto:

| Caso | Situação | Correção |
|---|---|---|
| 1 | irmão vermelho | recolore e rotação no pai; vira o caso 2, 3 ou 4 |
| 2 | irmão preto com os dois filhos pretos | irmão fica vermelho; o problema sobe para o pai |
| 3 | irmão preto, sobrinho de perto vermelho | rotação no irmão; vira o caso 4 |
| 4 | irmão preto, sobrinho de longe vermelho | recolore e rotação no pai; fim |

No máximo 3 rotações por remoção. Cada caso tem a versão espelhada (esquerda ↔ direita).

Com `RubroNegra(verbose=True)` a árvore imprime cada caso, e o desenho marca cada nó com `[V]` (vermelho) ou `[P]` (preto). Os mesmos 7 pedidos em ordem:

```
  inserir 1
  inserir 2
  inserir 3
    [Rubro-Negra] caso 3 em #3: tio preto em linha reta -> recolore e rotação no avô #1
    [Rubro-Negra] rotação à esquerda em #1 (#2 sobe)
  inserir 4
    [Rubro-Negra] caso 1 em #4: tio #1 vermelho -> recolore e sobe para o avô #2
  inserir 5
    [Rubro-Negra] caso 3 em #5: tio preto em linha reta -> recolore e rotação no avô #3
    [Rubro-Negra] rotação à esquerda em #3 (#4 sobe)
  inserir 6
    [Rubro-Negra] caso 1 em #6: tio #3 vermelho -> recolore e sobe para o avô #4
  inserir 7
    [Rubro-Negra] caso 3 em #7: tio preto em linha reta -> recolore e rotação no avô #5
    [Rubro-Negra] rotação à esquerda em #5 (#6 sobe)

        ┌── #7 [V]
    ┌── #6 [P]
    │   └── #5 [V]
┌── #4 [V]
│   └── #3 [P]
#2 [P]
└── #1 [P]
```

| Mesmos pedidos, em ordem | BST | AVL | Rubro-Negra |
|---|---:|---:|---:|
| 7 pedidos: altura | 7 | 3 | 4 |
| 7 pedidos: rotações | 0 | 4 | 3 |
| Base real (2.186 pedidos): altura | 2.186 | 12 | 20 |

A Rubro-Negra fica mais alta que a AVL (20 contra 12 níveis na base real), mas dentro do limite de 2 · log2(2.187) ≈ 22,2.

## A lanchonete

[`src/lanchonete.py`](src/lanchonete.py) traduz cada pedido do dia a dia numa operação da árvore. A árvore é escolhida na criação (`Lanchonete(AVL)`, `Lanchonete(BST)`...), então o mesmo código roda sobre as três.

| Método | Operação na árvore | O que faz |
|---|---|---|
| `novo_pedido` | inserção | registra com o próximo número; recusa item fora do cardápio |
| `consultar` | busca | devolve o pedido, ou nada se ele não existe ou foi cancelado |
| `cancelar` | remoção | só pedido em preparo; entregue não cancela |
| `proximo_a_preparar` / `entregar_proximo` | sucessor | a cozinha atende em ordem de chegada |
| `em_preparo` | intervalo | painel da cozinha: do último entregue até o último número |
| `pedido_seguinte` | sucessor | o pedido registrado logo depois de um número (cancelados não contam) |
| `pedidos_entre` / `fechamento` | intervalo | pedidos de um trecho de números e o total vendido |

Como a cozinha entrega em ordem, todo pedido até o último entregue está entregue, e todo pedido acima dele está em preparo. Por isso o próximo a preparar é o **sucessor** do último entregue, em O(log n), sem percorrer a lista de pedidos. Cancelados já saíram da árvore, e o sucessor pula por cima deles. O número do caixa nunca volta atrás, nem depois de um cancelamento.

`Lanchonete.da_base()` reproduz a semana do CSV: registra os 2.186 pedidos em ordem e depois cancela os 165 cancelados.

## Demonstração

`python main.py` mostra, desenhando as árvores no terminal:

1. **BST com 7 pedidos em ordem** vira uma escada (altura 7).
2. **AVL e Rubro-Negra** com os mesmos pedidos: cada caso, rotação e recoloração (altura 3 e 4).
3. **Cancelamentos** dos 3 primeiros pedidos: a BST continua torta, e AVL e Rubro-Negra se reorganizam.
4. **A semana inteira** nas três árvores, com os limites teóricos ao lado:

   | 2.186 pedidos em ordem | BST | AVL | Rubro-Negra |
   |---|---:|---:|---:|
   | altura | 2.186 | 12 | 20 |
   | comparações por busca (média) | 1.093,50 | 10,13 | 10,68 |
   | rotações (inserções e cancelamentos) | 0 | 2.174 | 2.171 |
   | recolorações | - | - | 11.528 |
   | altura depois dos 165 cancelamentos | 2.021 | 12 | 14 |

   Altura mínima possível: 12 · limite da AVL: 15,7 · limite da Rubro-Negra: 22,2.

5. **A lanchonete funcionando** sobre a AVL: pedidos novos, pedido recusado, painel da cozinha, consulta, cancelamento, entrega e fechamento de caixa de segunda-feira (304 pedidos entregues, R$ 12.529,00).

A saída é forçada para UTF-8, para os desenhos (`┌──`) aparecerem no terminal do Windows.

## Testes

Depois das operações, `validar()` confere as regras da árvore, e o conteúdo é comparado com um dicionário comum, que serve de resultado esperado.

- **Todas as árvores** ([`test_arvores.py`](tests/test_arvores.py)): árvore vazia, número repetido, remoção de folha, nó com um filho e nó com dois filhos, 3.000 inserções e remoções misturadas, sucessor e intervalo. Aqui `validar()` confere a ordem das chaves e o tamanho.
- **AVL** ([`test_avl.py`](tests/test_avl.py)): um teste para cada um dos 4 casos de rotação, o caso de filho equilibrado na remoção, no máximo 2 rotações por inserção, altura dentro do limite teórico e mínima com números em ordem. Aqui `validar()` também confere a altura guardada e o fator de cada nó; um teste monta uma árvore desequilibrada à mão para garantir que a validação acusa o erro.
- **Rubro-Negra** ([`test_rubro_negra.py`](tests/test_rubro_negra.py)): os 3 casos de inserção (com os espelhos) e os 4 casos de remoção, cada um num exemplo pequeno; no máximo 2 rotações por inserção e 3 por remoção; altura dentro do limite teórico. Aqui `validar()` confere as 5 regras, a sentinela e o ponteiro para o pai de cada nó; um teste quebra cada regra à mão para garantir que a validação acusa o erro.
- **Lanchonete** ([`test_lanchonete.py`](tests/test_lanchonete.py)): cada regra (novo pedido, recusa, cancelamento, entrega em ordem, painel, fechamento) roda sobre as três árvores e precisa dar o mesmo resultado nas três; a demonstração inteira roda sem erro.

## Integrantes

| Matrícula | Nome |
|---|---|
| 231011097 | André Meyer |
