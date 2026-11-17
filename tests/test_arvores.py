"""Testes de corretude das árvores.

Roda com (na raiz do projeto): python -m unittest -v

Os testes comuns rodam em todas as estruturas de ESTRUTURAS. Depois das
operações, validar() confere as regras da árvore e o conteúdo é comparado com
um dicionário comum, que serve de resultado esperado.
"""

import random
import unittest

from src.arvores import BST, ESTRUTURAS

SEMENTE = 42


class TesteArvore(unittest.TestCase):
    def conferir(self, arvore, modelo):
        """A árvore precisa seguir as próprias regras e ter exatamente o conteúdo do dicionário."""
        arvore.validar()
        self.assertEqual(len(arvore), len(modelo))
        self.assertEqual(list(arvore.em_ordem()), sorted(modelo.items()))


class TestOperacoesComuns(TesteArvore):
    def test_arvore_vazia(self):
        for Arvore in ESTRUTURAS:
            with self.subTest(Arvore.nome):
                arvore = Arvore()
                self.assertEqual(len(arvore), 0)
                self.assertEqual(arvore.altura(), 0)
                self.assertIsNone(arvore.buscar(1))
                self.assertNotIn(1, arvore)
                self.assertIsNone(arvore.minimo())
                self.assertIsNone(arvore.maximo())
                self.assertIsNone(arvore.sucessor(1))
                self.assertEqual(arvore.intervalo(1, 10), [])
                self.assertFalse(arvore.remover(1))
                self.assertEqual(arvore.desenhar(), "(árvore vazia)")
                arvore.validar()

    def test_pedidos_em_ordem(self):
        for Arvore in ESTRUTURAS:
            with self.subTest(Arvore.nome):
                arvore, modelo = Arvore(), {}
                for numero in range(1, 501):
                    self.assertTrue(arvore.inserir(numero, f"pedido {numero}"))
                    modelo[numero] = f"pedido {numero}"
                    arvore.validar()
                self.conferir(arvore, modelo)

    def test_pedidos_fora_de_ordem_e_busca(self):
        numeros = list(range(1, 1001))
        random.Random(SEMENTE).shuffle(numeros)
        for Arvore in ESTRUTURAS:
            with self.subTest(Arvore.nome):
                arvore, modelo = Arvore(), {}
                for numero in numeros:
                    arvore.inserir(numero, numero * 10)
                    modelo[numero] = numero * 10
                self.conferir(arvore, modelo)
                for numero in numeros:
                    self.assertEqual(arvore.buscar(numero), numero * 10)
                    self.assertIn(numero, arvore)
                self.assertIsNone(arvore.buscar(0))
                self.assertIsNone(arvore.buscar(1001))

    def test_numero_repetido_e_recusado(self):
        for Arvore in ESTRUTURAS:
            with self.subTest(Arvore.nome):
                arvore = Arvore()
                self.assertTrue(arvore.inserir(7, "original"))
                self.assertFalse(arvore.inserir(7, "repetido"))
                self.assertEqual(arvore.buscar(7), "original")
                self.assertEqual(len(arvore), 1)
                arvore.validar()

    def test_remocao_de_folha_um_filho_e_dois_filhos(self):
        #            50
        #       30        70
        #     20  40    60  80
        #        35
        for Arvore in ESTRUTURAS:
            with self.subTest(Arvore.nome):
                arvore, modelo = Arvore(), {}
                for numero in (50, 30, 70, 20, 40, 60, 80, 35):
                    arvore.inserir(numero, str(numero))
                    modelo[numero] = str(numero)
                for numero in (20, 40, 50, 30, 70, 35, 60, 80):
                    self.assertTrue(arvore.remover(numero))
                    del modelo[numero]
                    self.assertFalse(arvore.remover(numero))
                    self.conferir(arvore, modelo)
                self.assertEqual(arvore.altura(), 0)

    def test_insercoes_e_remocoes_misturadas(self):
        for Arvore in ESTRUTURAS:
            with self.subTest(Arvore.nome):
                rng = random.Random(SEMENTE)
                arvore, modelo = Arvore(), {}
                for _ in range(3000):
                    numero = rng.randint(1, 300)
                    if rng.random() < 0.6:
                        self.assertEqual(arvore.inserir(numero, -numero), numero not in modelo)
                        modelo.setdefault(numero, -numero)
                    else:
                        self.assertEqual(arvore.remover(numero), numero in modelo)
                        modelo.pop(numero, None)
                    arvore.validar()
                self.conferir(arvore, modelo)

    def test_minimo_maximo_e_sucessor(self):
        pares = list(range(2, 401, 2))
        random.Random(SEMENTE).shuffle(pares)
        for Arvore in ESTRUTURAS:
            with self.subTest(Arvore.nome):
                arvore = Arvore()
                for numero in pares:
                    arvore.inserir(numero)
                self.assertEqual(arvore.minimo(), 2)
                self.assertEqual(arvore.maximo(), 400)
                for numero in range(0, 402):
                    esperado = min((p for p in pares if p > numero), default=None)
                    self.assertEqual(arvore.sucessor(numero), esperado, f"sucessor de {numero}")

    def test_intervalo(self):
        numeros = random.Random(SEMENTE).sample(range(1, 2000), 500)
        consultas = [(1, 1999), (100, 200), (150, 150), (0, 0), (2000, 3000), (300, 100), (-5, 20)]
        for Arvore in ESTRUTURAS:
            with self.subTest(Arvore.nome):
                arvore = Arvore()
                for numero in numeros:
                    arvore.inserir(numero, str(numero))
                for inicio, fim in consultas:
                    esperado = [(n, str(n)) for n in sorted(numeros) if inicio <= n <= fim]
                    self.assertEqual(arvore.intervalo(inicio, fim), esperado, f"intervalo {inicio}..{fim}")

    def test_medir_busca_nao_altera_contador(self):
        for Arvore in ESTRUTURAS:
            with self.subTest(Arvore.nome):
                arvore = Arvore()
                for numero in (2, 1, 3):
                    arvore.inserir(numero)
                antes = arvore.comparacoes
                self.assertGreater(arvore.comparacoes_medias_busca([1, 2, 3]), 0)
                self.assertEqual(arvore.comparacoes, antes)


class TestBST(TesteArvore):
    def test_pedidos_em_ordem_viram_lista(self):
        """O pior caso: cada pedido novo vai para a direita do anterior."""
        n = 5000
        arvore = BST()
        for numero in range(1, n + 1):
            arvore.inserir(numero)
        self.assertEqual(arvore.altura(), n)
        # achar o pedido k custa k comparações: a média é (n + 1) / 2
        self.assertEqual(arvore.comparacoes_medias_busca(list(range(1, n + 1))), (n + 1) / 2)
        self.assertEqual(arvore.rotacoes, 0)
        arvore.validar()  # percorrer 5.000 níveis não pode estourar a recursão
        for numero in range(1, n + 1, 2):
            arvore.remover(numero)
        self.assertEqual(arvore.altura(), n // 2)  # remover não conserta a altura
        arvore.validar()

    def test_pedidos_embaralhados_ficam_baixos(self):
        numeros = list(range(1, 5001))
        random.Random(SEMENTE).shuffle(numeros)
        arvore = BST()
        for numero in numeros:
            arvore.inserir(numero)
        self.assertLess(arvore.altura(), 50)

    def test_desenho(self):
        arvore = BST()
        for numero in (4, 2, 6, 1, 3, 5, 7):
            arvore.inserir(numero)
        esperado = "\n".join(
            [
                "    ┌── #7",
                "┌── #6",
                "│   └── #5",
                "#4",
                "│   ┌── #3",
                "└── #2",
                "    └── #1",
            ]
        )
        self.assertEqual(arvore.desenhar(), esperado)
        self.assertIn("grande demais", arvore.desenhar(max_nos=3))


if __name__ == "__main__":
    unittest.main()
