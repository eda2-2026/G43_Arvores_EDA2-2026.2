"""Testes específicos da Rubro-Negra: os casos de inserção e remoção, as 5 regras e a altura.

As operações comuns (busca, remoção, sucessor, intervalo...) já rodam na
Rubro-Negra em test_arvores.py, porque ela está em ESTRUTURAS.
"""

import io
import math
import random
import unittest
from contextlib import redirect_stdout

from src.arvores import RubroNegra
from src.arvores.rubro_negra import PRETO, VERMELHO
from src.pedidos import carregar_pedidos

SEMENTE = 42


def montar(numeros, verbose=False):
    """Insere os números e devolve (árvore, texto impresso no modo passo a passo)."""
    arvore, saida = RubroNegra(verbose=verbose), io.StringIO()
    with redirect_stdout(saida):
        for numero in numeros:
            arvore.inserir(numero)
    return arvore, saida.getvalue()


def remover(arvore, numero):
    """Remove no modo passo a passo e devolve o texto impresso."""
    arvore.verbose, saida = True, io.StringIO()
    with redirect_stdout(saida):
        arvore.remover(numero)
    arvore.verbose = False
    return saida.getvalue()


def cores(arvore):
    """{número: 'V' ou 'P'} de todos os nós."""
    resultado, pilha = {}, [arvore.raiz]
    while pilha:
        no = pilha.pop()
        if no is not arvore._nil:
            resultado[no.chave] = "V" if no.cor == VERMELHO else "P"
            pilha += [no.esq, no.dir]
    return resultado


class TestCasosDeInsercao(unittest.TestCase):
    def test_caso_1_tio_vermelho_so_recolore(self):
        arvore, saida = montar([2, 1, 3, 4], verbose=True)
        arvore.validar()
        self.assertIn("caso 1 em #4: tio #1 vermelho", saida)
        self.assertEqual(arvore.rotacoes, 0)
        self.assertEqual(cores(arvore), {2: "P", 1: "P", 3: "P", 4: "V"})

    def test_caso_3_linha_reta_uma_rotacao(self):
        for numeros in ([3, 2, 1], [1, 2, 3]):  # e o espelho
            with self.subTest(numeros):
                arvore, saida = montar(numeros, verbose=True)
                arvore.validar()
                self.assertIn("caso 3", saida)
                self.assertNotIn("caso 2", saida)
                self.assertEqual(arvore.rotacoes, 1)
                self.assertEqual(cores(arvore), {2: "P", 1: "V", 3: "V"})

    def test_caso_2_joelho_vira_caso_3(self):
        for numeros in ([3, 1, 2], [1, 3, 2]):  # e o espelho
            with self.subTest(numeros):
                arvore, saida = montar(numeros, verbose=True)
                arvore.validar()
                self.assertLess(saida.index("caso 2"), saida.index("caso 3"))
                self.assertEqual(arvore.rotacoes, 2)
                self.assertEqual(cores(arvore), {2: "P", 1: "V", 3: "V"})

    def test_no_maximo_duas_rotacoes_por_insercao(self):
        numeros = list(range(1, 2001))
        random.Random(SEMENTE).shuffle(numeros)
        arvore = RubroNegra()
        for numero in numeros:
            antes = arvore.rotacoes
            arvore.inserir(numero)
            self.assertLessEqual(arvore.rotacoes - antes, 2)


class TestCasosDeRemocao(unittest.TestCase):
    def test_remover_vermelho_nao_precisa_corrigir(self):
        arvore, _ = montar([2, 1, 3, 4])
        saida = remover(arvore, 4)  # #4 é vermelho
        arvore.validar()
        self.assertEqual(saida, "")
        self.assertEqual(arvore.rotacoes, 0)

    def test_caso_1_irmao_vermelho(self):
        arvore, _ = montar([1, 2, 3, 4, 5, 6])
        saida = remover(arvore, 1)
        arvore.validar()
        self.assertIn("remoção caso 1: irmão #4 vermelho", saida)
        self.assertLess(saida.index("caso 1"), saida.index("caso 2"))  # depois do caso 1 vem outro caso
        self.assertEqual(arvore.chaves(), [2, 3, 4, 5, 6])

    def test_caso_2_irmao_com_filhos_pretos(self):
        arvore, _ = montar([2, 1, 3, 4])
        remover(arvore, 4)
        saida = remover(arvore, 1)
        arvore.validar()
        self.assertIn("remoção caso 2: irmão #3", saida)
        self.assertEqual(arvore.rotacoes, 0)
        self.assertEqual(cores(arvore), {2: "P", 3: "V"})

    def test_caso_3_sobrinho_de_perto_vira_caso_4(self):
        arvore, _ = montar([2, 1, 4, 3])
        saida = remover(arvore, 1)
        arvore.validar()
        self.assertLess(saida.index("remoção caso 3"), saida.index("remoção caso 4"))
        self.assertEqual(arvore.rotacoes, 2)
        self.assertEqual(cores(arvore), {3: "P", 2: "P", 4: "P"})

    def test_caso_4_sobrinho_de_longe(self):
        arvore, _ = montar([2, 1, 3, 4])
        saida = remover(arvore, 1)
        arvore.validar()
        self.assertIn("remoção caso 4: sobrinho de longe #4", saida)
        self.assertNotIn("caso 3", saida)
        self.assertEqual(arvore.rotacoes, 1)
        self.assertEqual(cores(arvore), {3: "P", 2: "P", 4: "P"})

    def test_todos_os_casos_aparecem_e_no_maximo_tres_rotacoes(self):
        """Remove metade de 2.000 pedidos: cada remoção usa no máximo 3 rotações."""
        numeros = list(range(1, 2001))
        rng = random.Random(SEMENTE)
        rng.shuffle(numeros)
        arvore, _ = montar(numeros)
        casos_vistos = set()
        for numero in rng.sample(numeros, 1000):
            antes = arvore.rotacoes
            saida = remover(arvore, numero)
            self.assertLessEqual(arvore.rotacoes - antes, 3)
            casos_vistos |= {caso for caso in "1234" if f"remoção caso {caso}" in saida}
            arvore.validar()
        self.assertEqual(casos_vistos, set("1234"))


class TestAlturaDaRubroNegra(unittest.TestCase):
    def test_altura_dentro_do_limite_teorico(self):
        """Em qualquer ordem, a altura fica no máximo em 2 * log2(n + 1)."""
        rng = random.Random(SEMENTE)
        for n in (10, 100, 1000, 5000):
            numeros = list(range(1, n + 1))
            for ordem in ("em ordem", "embaralhado"):
                if ordem == "embaralhado":
                    rng.shuffle(numeros)
                with self.subTest(n=n, ordem=ordem):
                    arvore, _ = montar(numeros)
                    self.assertLessEqual(arvore.altura(), 2 * math.log2(n + 1))

    def test_base_real(self):
        pedidos = carregar_pedidos()
        arvore = RubroNegra()
        for pedido in pedidos:
            arvore.inserir(pedido.numero, pedido)
        arvore.validar()
        self.assertEqual(arvore.altura(), 20)  # AVL: 12 | BST: 2.186 | limite: 22,2
        for pedido in pedidos:
            if pedido.status == "cancelado":
                arvore.remover(pedido.numero)
        arvore.validar()
        self.assertEqual(len(arvore), len(pedidos) - 165)


class TestValidacaoEDesenho(unittest.TestCase):
    def test_validar_detecta_cada_regra_quebrada(self):
        arvore, _ = montar([2, 1, 3])  # 2 preto, 1 e 3 vermelhos
        arvore.raiz.cor = VERMELHO
        with self.assertRaisesRegex(AssertionError, "raiz não é preta"):
            arvore.validar()

        arvore, _ = montar([2, 1, 3, 4])  # 3 preto com o 4 vermelho embaixo
        arvore.raiz.dir.cor = VERMELHO
        arvore.raiz.esq.cor = VERMELHO
        with self.assertRaisesRegex(AssertionError, "vermelho com filho vermelho"):
            arvore.validar()

        arvore, _ = montar([2, 1, 3])
        arvore.raiz.esq.cor = PRETO  # o caminho pela esquerda ganha um preto a mais
        with self.assertRaisesRegex(AssertionError, "altura preta diferente"):
            arvore.validar()

    def test_desenho_mostra_as_cores(self):
        arvore, _ = montar(range(1, 8))
        esperado = "\n".join(
            [
                "        ┌── #7 [V]",
                "    ┌── #6 [P]",
                "    │   └── #5 [V]",
                "┌── #4 [V]",
                "│   └── #3 [P]",
                "#2 [P]",
                "└── #1 [P]",
            ]
        )
        self.assertEqual(arvore.desenhar(), esperado)
        self.assertEqual((arvore.altura(), arvore.rotacoes, arvore.recoloracoes), (4, 3, 14))


if __name__ == "__main__":
    unittest.main()
