"""Parte comum das árvores de busca da lanchonete.

A chave de cada nó é o número do pedido e o valor é o próprio Pedido.

Tudo o que só CONSULTA a árvore (buscar, mínimo, máximo, sucessor, intervalo,
percurso em ordem, altura e desenho) é igual em qualquer árvore binária de
busca e fica aqui. Cada árvore implementa só o que muda: inserir, remover e
validar as próprias regras.

`self._nil` é o "nó vazio" (None por padrão). Uma árvore que use um nó
sentinela no lugar de None só precisa redefinir `_criar_nil`: os métodos
daqui comparam sempre com `self._nil` e continuam valendo.

Os métodos são iterativos de propósito: com os pedidos chegando em ordem
(1, 2, 3...) a BST vira uma lista com milhares de níveis, e uma recursão
desse tamanho estoura o limite do Python.
"""

from collections import deque


class No:
    __slots__ = ("chave", "valor", "esq", "dir")

    def __init__(self, chave, valor=None, nil=None):
        self.chave = chave
        self.valor = valor
        self.esq = nil
        self.dir = nil


class ArvoreBusca:
    nome = "Árvore"

    def __init__(self, verbose=False):
        self._nil = self._criar_nil()
        self.raiz = self._nil  # árvore vazia: a raiz é o próprio nó vazio
        self.tamanho = 0
        self.verbose = verbose  # True: imprime cada caso e cada rotação (passo a passo)
        self.comparacoes = 0  # comparações de chave feitas em buscas e inserções
        self.rotacoes = 0

    def _criar_nil(self):
        return None

    def _log(self, mensagem):
        if self.verbose:
            print(f"    [{self.nome}] {mensagem}")

    def __len__(self):
        return self.tamanho

    def __contains__(self, chave):
        return self._buscar_no(chave) is not self._nil

    def zerar_contadores(self):
        self.comparacoes = 0
        self.rotacoes = 0

    # ------------------------------------------------------------------
    # Implementados em cada árvore
    # ------------------------------------------------------------------
    def inserir(self, chave, valor=None):
        """Insere a chave. Devolve False se ela já existe (número repetido)."""
        raise NotImplementedError

    def remover(self, chave):
        """Remove a chave. Devolve False se ela não existe."""
        raise NotImplementedError

    def validar(self):
        """Confere as regras da árvore. Levanta AssertionError se alguma falhar."""
        self._validar_ordem()

    # ------------------------------------------------------------------
    # Busca
    # ------------------------------------------------------------------
    def _buscar_no(self, chave):
        atual = self.raiz
        while atual is not self._nil:
            self.comparacoes += 1
            if chave == atual.chave:
                return atual
            atual = atual.esq if chave < atual.chave else atual.dir
        return self._nil

    def buscar(self, chave):
        """Valor guardado na chave, ou None se a chave não existe."""
        no = self._buscar_no(chave)
        return None if no is self._nil else no.valor

    def _minimo_no(self, no):
        while no.esq is not self._nil:
            no = no.esq
        return no

    def _maximo_no(self, no):
        while no.dir is not self._nil:
            no = no.dir
        return no

    def minimo(self):
        """Menor chave (o pedido mais antigo), ou None se a árvore está vazia."""
        return None if self.raiz is self._nil else self._minimo_no(self.raiz).chave

    def maximo(self):
        """Maior chave (o pedido mais recente), ou None se a árvore está vazia."""
        return None if self.raiz is self._nil else self._maximo_no(self.raiz).chave

    def sucessor(self, chave):
        """Menor chave MAIOR que `chave`, ou None. A chave não precisa estar na árvore.

        Desce da raiz guardando o último nó em que virou à esquerda: ele é o
        menor valor visto que ainda é maior que a chave procurada.
        """
        atual, candidato = self.raiz, None
        while atual is not self._nil:
            self.comparacoes += 1
            if atual.chave > chave:
                candidato = atual.chave
                atual = atual.esq
            else:
                atual = atual.dir
        return candidato

    def intervalo(self, inicio, fim):
        """Lista de (chave, valor) com inicio <= chave <= fim, em ordem crescente.

        É um percurso em ordem que não entra nos ramos que não podem ter
        chaves no intervalo, e para assim que passa de `fim`.
        """
        resultado, pilha, atual = [], [], self.raiz
        while True:
            # desce pela esquerda só enquanto ainda pode haver chave >= inicio
            while atual is not self._nil:
                pilha.append(atual)
                atual = atual.esq if atual.chave > inicio else self._nil
            if not pilha:
                return resultado
            no = pilha.pop()
            if no.chave > fim:
                return resultado
            if no.chave >= inicio:
                resultado.append((no.chave, no.valor))
            atual = no.dir

    # ------------------------------------------------------------------
    # Percurso e medidas
    # ------------------------------------------------------------------
    def em_ordem(self):
        """Gera (chave, valor) em ordem crescente de chave."""
        pilha, atual = [], self.raiz
        while pilha or atual is not self._nil:
            while atual is not self._nil:
                pilha.append(atual)
                atual = atual.esq
            atual = pilha.pop()
            yield atual.chave, atual.valor
            atual = atual.dir

    def chaves(self):
        return [chave for chave, _ in self.em_ordem()]

    def altura(self):
        """Número de níveis (árvore vazia = 0, só a raiz = 1). Percorre nível a nível."""
        if self.raiz is self._nil:
            return 0
        niveis, fila = 0, deque([self.raiz])
        while fila:
            niveis += 1
            for _ in range(len(fila)):
                no = fila.popleft()
                if no.esq is not self._nil:
                    fila.append(no.esq)
                if no.dir is not self._nil:
                    fila.append(no.dir)
        return niveis

    def comparacoes_medias_busca(self, chaves):
        """Média de comparações para buscar cada chave da lista (não suja o contador)."""
        if not chaves:
            return 0.0
        antes = self.comparacoes
        for chave in chaves:
            self._buscar_no(chave)
        media = (self.comparacoes - antes) / len(chaves)
        self.comparacoes = antes
        return media

    # ------------------------------------------------------------------
    # Desenho no terminal
    # ------------------------------------------------------------------
    def _rotulo(self, no):
        """Texto de cada nó no desenho. As árvores balanceadas acrescentam informação."""
        return f"#{no.chave}"

    def desenhar(self, max_nos=40):
        """Árvore deitada: raiz à esquerda, filho direito acima e filho esquerdo abaixo."""
        if self.raiz is self._nil:
            return "(árvore vazia)"
        if self.tamanho > max_nos:
            return f"(árvore com {self.tamanho} nós: grande demais para desenhar)"

        linhas = []
        # a pilha guarda nós a desenhar (no, prefixo, lado) ou linhas já prontas (str)
        pilha = [(self.raiz, "", "raiz")]
        while pilha:
            item = pilha.pop()
            if isinstance(item, str):
                linhas.append(item)
                continue
            no, prefixo, lado = item
            # a barra "│" liga o nó ao pai: aparece no lado que fica entre os dois
            if lado == "raiz":
                conector, prefixo_dir, prefixo_esq = "", "", ""
            elif lado == "dir":
                conector, prefixo_dir, prefixo_esq = "┌── ", prefixo + "    ", prefixo + "│   "
            else:
                conector, prefixo_dir, prefixo_esq = "└── ", prefixo + "│   ", prefixo + "    "
            # saída desejada: subárvore direita, o nó, subárvore esquerda (a pilha inverte)
            if no.esq is not self._nil:
                pilha.append((no.esq, prefixo_esq, "esq"))
            pilha.append(prefixo + conector + self._rotulo(no))
            if no.dir is not self._nil:
                pilha.append((no.dir, prefixo_dir, "dir"))
        return "\n".join(linhas)

    # ------------------------------------------------------------------
    # Validação comum
    # ------------------------------------------------------------------
    def _validar_ordem(self):
        """Em ordem, as chaves precisam sair estritamente crescentes, e na quantidade certa."""
        anterior, quantidade = None, 0
        for chave, _ in self.em_ordem():
            assert anterior is None or anterior < chave, f"chave #{chave} fora de ordem"
            anterior = chave
            quantidade += 1
        assert quantidade == self.tamanho, f"tamanho diz {self.tamanho}, mas há {quantidade} nós"
