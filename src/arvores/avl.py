"""Árvore AVL (Adelson-Velsky e Landis, 1962).

É uma BST que se rebalanceia sozinha. Cada nó guarda a própria altura, e o
fator de balanceamento é:

    fator = altura(esquerda) - altura(direita)

Regra da AVL: em todo nó o fator fica entre -1 e +1. Isso limita a altura a
cerca de 1,44 * log2(n), então busca, inserção e remoção custam O(log n).

Depois de inserir ou remover, a volta da recursão recalcula a altura de cada
nó do caminho. Se algum ficou com fator +2 ou -2, aplica a rotação do caso:

    caso               fator do nó   fator do filho   correção
    esquerda-esquerda      +2        >= 0 (esquerdo)  rotação à direita
    esquerda-direita       +2         < 0 (esquerdo)  esquerda no filho, depois direita
    direita-direita        -2        <= 0 (direito)   rotação à esquerda
    direita-esquerda       -2         > 0 (direito)   direita no filho, depois esquerda

O filho com fator 0 só aparece na remoção; na inserção ele sempre pende para
um dos lados.

Como a altura é O(log n), a recursão é rasa e pode ser usada sem risco.
"""

from .base import ArvoreBusca, No


class NoAVL(No):
    __slots__ = ("altura",)

    def __init__(self, chave, valor=None):
        super().__init__(chave, valor)
        self.altura = 1  # folha tem altura 1 (subárvore vazia tem altura 0)


def _altura(no):
    return 0 if no is None else no.altura


def _fator(no):
    return _altura(no.esq) - _altura(no.dir)


def _atualizar_altura(no):
    no.altura = 1 + max(_altura(no.esq), _altura(no.dir))


class AVL(ArvoreBusca):
    nome = "AVL"

    # ------------------------------------------------------------------
    # Rotações: devolvem a nova raiz da subárvore
    # ------------------------------------------------------------------
    def _rotacao_direita(self, y):
        """
                y               x
               / \\             / \\
              x   C    ->     A   y
             / \\                 / \\
            A   B               B   C
        """
        x = y.esq
        y.esq = x.dir
        x.dir = y
        _atualizar_altura(y)  # y desceu: atualiza antes de x, que agora está acima
        _atualizar_altura(x)
        self.rotacoes += 1
        self._log(f"rotação à direita em #{y.chave} (#{x.chave} sobe)")
        return x

    def _rotacao_esquerda(self, x):
        """
              x                   y
             / \\                 / \\
            A   y      ->       x   C
               / \\             / \\
              B   C           A   B
        """
        y = x.dir
        x.dir = y.esq
        y.esq = x
        _atualizar_altura(x)
        _atualizar_altura(y)
        self.rotacoes += 1
        self._log(f"rotação à esquerda em #{x.chave} (#{y.chave} sobe)")
        return y

    def _balancear(self, no):
        """Recalcula a altura de `no` e, se o fator saiu de [-1, +1], aplica a rotação do caso."""
        _atualizar_altura(no)
        fator = _fator(no)

        if fator > 1:  # pesado à esquerda
            if _fator(no.esq) < 0:
                self._log(f"caso esquerda-direita em #{no.chave} (fator {fator:+d})")
                no.esq = self._rotacao_esquerda(no.esq)
            else:
                self._log(f"caso esquerda-esquerda em #{no.chave} (fator {fator:+d})")
            return self._rotacao_direita(no)

        if fator < -1:  # pesado à direita
            if _fator(no.dir) > 0:
                self._log(f"caso direita-esquerda em #{no.chave} (fator {fator:+d})")
                no.dir = self._rotacao_direita(no.dir)
            else:
                self._log(f"caso direita-direita em #{no.chave} (fator {fator:+d})")
            return self._rotacao_esquerda(no)

        return no

    # ------------------------------------------------------------------
    # Inserção
    # ------------------------------------------------------------------
    def inserir(self, chave, valor=None):
        tamanho_antes = self.tamanho
        self.raiz = self._inserir(self.raiz, chave, valor)
        return self.tamanho > tamanho_antes

    def _inserir(self, no, chave, valor):
        if no is None:
            self.tamanho += 1
            return NoAVL(chave, valor)
        self.comparacoes += 1
        if chave == no.chave:
            return no  # número de pedido já existe: nada muda
        if chave < no.chave:
            no.esq = self._inserir(no.esq, chave, valor)
        else:
            no.dir = self._inserir(no.dir, chave, valor)
        return self._balancear(no)

    # ------------------------------------------------------------------
    # Remoção
    # ------------------------------------------------------------------
    def remover(self, chave):
        tamanho_antes = self.tamanho
        self.raiz = self._remover(self.raiz, chave)
        return self.tamanho < tamanho_antes

    def _remover(self, no, chave):
        if no is None:
            return None  # chave não existe
        self.comparacoes += 1
        if chave < no.chave:
            no.esq = self._remover(no.esq, chave)
        elif chave > no.chave:
            no.dir = self._remover(no.dir, chave)
        else:
            if no.esq is None or no.dir is None:
                # zero ou um filho: o filho (ou None) ocupa o lugar do nó
                self.tamanho -= 1
                return no.esq if no.esq is not None else no.dir
            # dois filhos: o sucessor (menor da direita) toma o lugar do nó
            # e é removido da subárvore direita
            sucessor = self._minimo_no(no.dir)
            no.chave, no.valor = sucessor.chave, sucessor.valor
            no.dir = self._remover(no.dir, sucessor.chave)
        return self._balancear(no)

    # ------------------------------------------------------------------
    # Desenho e validação
    # ------------------------------------------------------------------
    def _rotulo(self, no):
        return f"#{no.chave} [f={_fator(no):+d}]"

    def validar(self):
        super().validar()
        self._validar_no(self.raiz)

    def _validar_no(self, no):
        """Devolve a altura real da subárvore e confere a altura guardada e o fator de cada nó."""
        if no is None:
            return 0
        altura_esq = self._validar_no(no.esq)
        altura_dir = self._validar_no(no.dir)
        assert no.altura == 1 + max(altura_esq, altura_dir), f"altura guardada errada em #{no.chave}"
        assert abs(altura_esq - altura_dir) <= 1, f"fator {altura_esq - altura_dir:+d} em #{no.chave}"
        return no.altura
