"""Árvore binária de busca (BST) sem balanceamento.

Regra: chaves menores à esquerda, maiores à direita. Busca, inserção e
remoção custam O(h), onde h é a altura.

A BST nunca se reorganiza: a altura depende só da ordem de chegada. Com os
pedidos chegando em ordem (1, 2, 3...), cada número novo é maior que todos os
anteriores e vai sempre para a direita. A árvore vira uma lista com h = n.
"""

from .base import ArvoreBusca, No


class BST(ArvoreBusca):
    nome = "BST"

    def inserir(self, chave, valor=None):
        pai, atual = None, self.raiz
        while atual is not None:
            self.comparacoes += 1
            if chave == atual.chave:
                return False  # número de pedido já existe
            pai = atual
            atual = atual.esq if chave < atual.chave else atual.dir

        novo = No(chave, valor)
        if pai is None:
            self.raiz = novo
        elif chave < pai.chave:
            pai.esq = novo
        else:
            pai.dir = novo
        self.tamanho += 1
        return True

    def remover(self, chave):
        # 1. acha o nó, guardando o pai (a BST não tem ponteiro para o pai)
        pai, atual = None, self.raiz
        while atual is not None and atual.chave != chave:
            self.comparacoes += 1
            pai = atual
            atual = atual.esq if chave < atual.chave else atual.dir
        if atual is None:
            return False

        # 2. dois filhos: o sucessor (menor da direita) toma o lugar do nó,
        #    e quem sai da árvore passa a ser o sucessor, que tem no máximo um filho
        if atual.esq is not None and atual.dir is not None:
            pai_sucessor, sucessor = atual, atual.dir
            while sucessor.esq is not None:
                pai_sucessor, sucessor = sucessor, sucessor.esq
            atual.chave, atual.valor = sucessor.chave, sucessor.valor
            pai, atual = pai_sucessor, sucessor

        # 3. zero ou um filho: o filho (ou None) ocupa o lugar do nó
        filho = atual.esq if atual.esq is not None else atual.dir
        if pai is None:
            self.raiz = filho
        elif pai.esq is atual:
            pai.esq = filho
        else:
            pai.dir = filho
        self.tamanho -= 1
        return True
