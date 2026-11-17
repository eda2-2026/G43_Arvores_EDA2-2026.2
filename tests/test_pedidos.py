"""Testes da base de pedidos (dados/pedidos.csv) e do gerador."""

import csv
import unittest

from dados.gerar_base import DIAS, PEDIDOS_POR_DIA, gerar_pedidos
from src.arvores import BST
from src.pedidos import CAMINHO_BASE, CARDAPIO, carregar_pedidos


class TestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pedidos = carregar_pedidos()

    def test_arquivo_igual_ao_gerador(self):
        """O CSV do repositório é exatamente o que o gerador produz com a semente 42."""
        with open(CAMINHO_BASE, newline="", encoding="utf-8") as arquivo:
            linhas = list(csv.DictReader(arquivo))
        geradas = [{campo: str(valor) for campo, valor in p.items()} for p in gerar_pedidos()]
        self.assertEqual(linhas, geradas)

    def test_quantidade(self):
        minimo, maximo = PEDIDOS_POR_DIA
        self.assertTrue(DIAS * minimo <= len(self.pedidos) <= DIAS * maximo)

    def test_numeros_sequenciais_e_horarios_em_ordem(self):
        self.assertEqual([p.numero for p in self.pedidos], list(range(1, len(self.pedidos) + 1)))
        horarios = [p.data_hora for p in self.pedidos]
        self.assertEqual(horarios, sorted(horarios))

    def test_campos_validos(self):
        for pedido in self.pedidos:
            self.assertIn(pedido.status, ("entregue", "cancelado"))
            self.assertTrue(1 <= len(pedido.itens) <= 4)
            self.assertAlmostEqual(pedido.valor, sum(CARDAPIO[item] for item in pedido.itens))
            self.assertTrue(11 <= pedido.data_hora.hour < 23)

    def test_base_real_na_bst_vira_lista(self):
        """Na ordem do arquivo os números chegam crescentes: a BST fica com altura n."""
        arvore = BST()
        for pedido in self.pedidos:
            self.assertTrue(arvore.inserir(pedido.numero, pedido))
        self.assertEqual(arvore.altura(), len(self.pedidos))
        self.assertEqual(arvore.buscar(1), self.pedidos[0])


if __name__ == "__main__":
    unittest.main()
