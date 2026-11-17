"""Testes específicos da AVL: os 4 casos de rotação, a regra do fator e a altura.

As operações comuns (busca, remoção, sucessor, intervalo...) já rodam na AVL
em test_arvores.py, porque ela está em ESTRUTURAS.
"""

import io
import math
import random
import unittest
from contextlib import redirect_stdout

from src.arvores import AVL
from src.pedidos import carregar_pedidos

SEMENTE = 42


def montar(numeros, verbose=False):
    """Insere os números e devolve (árvore, texto impresso no modo passo a passo)."""
    arvore, saida = AVL(verbose=verbose), io.StringIO()
    with redirect_stdout(saida):
        for numero in numeros:
            arvore.inserir(numero)
    return arvore, saida.getvalue()


class TestCasosDeRotacao(unittest.TestCase):
    """Cada caso com 3 pedidos: o terceiro desequilibra a raiz e o #2 tem que subir."""

    def conferir_caso(self, numeros, caso, rotacoes):
        arvore, saida = montar(numeros, verbose=True)
        arvore.validar()
        self.assertIn(f"caso {caso} em #{numeros[0]}", saida)
        self.assertEqual(arvore.rotacoes, rotacoes)
        self.assertEqual(arvore.raiz.chave, 2)
        self.assertEqual(arvore.altura(), 2)

    def test_esquerda_esquerda_rotacao_simples_a_direita(self):
        self.conferir_caso([3, 2, 1], "esquerda-esquerda", rotacoes=1)

    def test_direita_direita_rotacao_simples_a_esquerda(self):
        self.conferir_caso([1, 2, 3], "direita-direita", rotacoes=1)

    def test_esquerda_direita_rotacao_dupla(self):
        self.conferir_caso([3, 1, 2], "esquerda-direita", rotacoes=2)

    def test_direita_esquerda_rotacao_dupla(self):
        self.conferir_caso([1, 3, 2], "direita-esquerda", rotacoes=2)

    def test_remocao_com_filho_equilibrado(self):
        """Fator 0 no filho só acontece na remoção: rotação simples resolve.

            2                    4
           / \\                  / \\
          1   4     remover 1   2   5
             / \\       ->        \\
            3   5                  3
        """
        arvore, _ = montar([2, 1, 4, 3, 5])
        saida = io.StringIO()
        arvore.verbose = True
        with redirect_stdout(saida):
            arvore.remover(1)
        arvore.validar()
        self.assertIn("caso direita-direita em #2", saida.getvalue())
        self.assertEqual(arvore.raiz.chave, 4)
        self.assertEqual(arvore.chaves(), [2, 3, 4, 5])

    def test_modo_silencioso_nao_imprime(self):
        _, saida = montar([1, 2, 3])
        self.assertEqual(saida, "")


class TestAlturaDaAVL(unittest.TestCase):
    def test_pedidos_em_ordem_dao_a_menor_altura_possivel(self):
        """Com os números em ordem, a AVL fica com floor(log2 n) + 1 níveis: o mínimo."""
        for n in (1, 7, 8, 100, 1000, 5000):
            arvore, _ = montar(range(1, n + 1))
            self.assertEqual(arvore.altura(), math.floor(math.log2(n)) + 1, f"n = {n}")

    def test_altura_dentro_do_limite_teorico(self):
        """Em qualquer ordem, a altura fica abaixo de ~1,44 * log2(n + 2)."""
        rng = random.Random(SEMENTE)
        for n in (10, 100, 1000, 5000):
            numeros = list(range(1, n + 1))
            rng.shuffle(numeros)
            arvore, _ = montar(numeros)
            self.assertLessEqual(arvore.altura(), 1.4405 * math.log2(n + 2) - 0.3277, f"n = {n}")

    def test_no_maximo_duas_rotacoes_por_insercao(self):
        """Na inserção, uma correção (simples ou dupla) no nó mais baixo já basta."""
        numeros = list(range(1, 2001))
        random.Random(SEMENTE).shuffle(numeros)
        arvore = AVL()
        for numero in numeros:
            antes = arvore.rotacoes
            arvore.inserir(numero)
            self.assertLessEqual(arvore.rotacoes - antes, 2)

    def test_remover_metade_mantem_a_regra(self):
        numeros = list(range(1, 2001))
        arvore, _ = montar(numeros)
        for numero in random.Random(SEMENTE).sample(numeros, 1000):
            arvore.remover(numero)
            arvore.validar()
        self.assertLessEqual(arvore.altura(), 1.4405 * math.log2(1000 + 2) - 0.3277)

    def test_base_real_fica_baixa(self):
        pedidos = carregar_pedidos()
        arvore = AVL()
        for pedido in pedidos:
            arvore.inserir(pedido.numero, pedido)
        arvore.validar()
        self.assertEqual(arvore.altura(), math.floor(math.log2(len(pedidos))) + 1)  # 12 níveis


class TestValidacaoEDesenho(unittest.TestCase):
    def test_validar_detecta_arvore_desequilibrada(self):
        """Pendura dois nós à mão, sem rebalancear: validar() tem que acusar o fator -2 no #3."""
        arvore, _ = montar([2, 1, 3])
        NoAVL = type(arvore.raiz)
        quatro, cinco = NoAVL(4), NoAVL(5)
        arvore.raiz.dir.dir, quatro.dir = quatro, cinco
        quatro.altura, arvore.raiz.dir.altura, arvore.raiz.altura = 2, 3, 4  # alturas certas
        arvore.tamanho = 5
        with self.assertRaisesRegex(AssertionError, r"fator -2 em #3"):
            arvore.validar()

    def test_desenho_mostra_o_fator(self):
        arvore, _ = montar([2, 1, 3, 4])
        esperado = "\n".join(
            [
                "    ┌── #4 [f=+0]",
                "┌── #3 [f=-1]",
                "#2 [f=-1]",
                "└── #1 [f=+0]",
            ]
        )
        self.assertEqual(arvore.desenhar(), esperado)


if __name__ == "__main__":
    unittest.main()
