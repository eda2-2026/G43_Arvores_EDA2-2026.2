"""Testes das regras da lanchonete. Cada teste roda sobre as três árvores."""

import io
import unittest
from contextlib import redirect_stdout
from datetime import datetime

import main
from src.arvores import ESTRUTURAS
from src.lanchonete import CANCELADO, EM_PREPARO, ENTREGUE, Lanchonete
from src.pedidos import carregar_pedidos, numero_br, reais

HORA = datetime(2026, 11, 23, 12, 0)


def loja_com_pedidos(Arvore, quantidade):
    loja = Lanchonete(Arvore)
    for i in range(quantidade):
        loja.novo_pedido(f"cliente {i + 1}", ["X-Burguer", "Refrigerante"], agora=HORA)
    return loja


class TestLanchonete(unittest.TestCase):
    def test_base_da_semana(self):
        pedidos = carregar_pedidos()
        cancelados = {p.numero for p in pedidos if p.status == CANCELADO}
        for Arvore in ESTRUTURAS:
            with self.subTest(Arvore.nome):
                loja = Lanchonete.da_base(Arvore)
                loja.arvore.validar()
                self.assertEqual(len(loja), len(pedidos) - len(cancelados))
                self.assertEqual(loja.proximo_numero, len(pedidos) + 1)
                self.assertIsNone(loja.proximo_a_preparar())  # a semana terminou com tudo entregue
                self.assertEqual(loja.em_preparo(), [])
                for numero in sorted(cancelados)[:10]:
                    self.assertIsNone(loja.consultar(numero))
                self.assertEqual(loja.consultar(1).status, ENTREGUE)

    def test_novo_pedido(self):
        for Arvore in ESTRUTURAS:
            with self.subTest(Arvore.nome):
                loja = Lanchonete(Arvore)
                pedido = loja.novo_pedido("Ana", ["X-Tudo", "Batata frita", "Batata frita"], agora=HORA)
                self.assertEqual((pedido.numero, pedido.valor, pedido.status), (1, 53.0, EM_PREPARO))
                self.assertIs(loja.consultar(1), pedido)
                self.assertEqual(loja.novo_pedido("Bia", ["Pastel"], agora=HORA).numero, 2)
                with self.assertRaisesRegex(ValueError, "Pizza"):
                    loja.novo_pedido("Caio", ["Pastel", "Pizza"], agora=HORA)
                with self.assertRaises(ValueError):
                    loja.novo_pedido("Caio", [], agora=HORA)
                self.assertEqual(len(loja), 2)  # pedido recusado não gasta número nem entra

    def test_cozinha_entrega_em_ordem_de_chegada(self):
        for Arvore in ESTRUTURAS:
            with self.subTest(Arvore.nome):
                loja = loja_com_pedidos(Arvore, 5)
                self.assertEqual([p.numero for p in loja.em_preparo()], [1, 2, 3, 4, 5])
                self.assertEqual(loja.proximo_a_preparar().numero, 1)
                self.assertEqual(loja.entregar_proximo().numero, 1)
                self.assertEqual(loja.entregar_proximo().numero, 2)
                self.assertEqual(loja.consultar(2).status, ENTREGUE)
                self.assertEqual([p.numero for p in loja.em_preparo()], [3, 4, 5])
                for _ in range(3):
                    loja.entregar_proximo()
                self.assertIsNone(loja.entregar_proximo())
                self.assertEqual(loja.em_preparo(), [])

    def test_cancelar(self):
        for Arvore in ESTRUTURAS:
            with self.subTest(Arvore.nome):
                loja = loja_com_pedidos(Arvore, 5)
                loja.entregar_proximo()  # #1 entregue
                self.assertIsNone(loja.cancelar(1))  # entregue não cancela
                self.assertIsNone(loja.cancelar(99))  # não existe
                cancelado = loja.cancelar(2)
                self.assertEqual(cancelado.status, CANCELADO)
                self.assertIsNone(loja.consultar(2))
                self.assertIsNone(loja.cancelar(2))  # já cancelado
                self.assertEqual(loja.proximo_a_preparar().numero, 3)  # o sucessor pula o #2
                loja.cancelar(5)
                self.assertEqual(loja.novo_pedido("Dani", ["Pastel"], agora=HORA).numero, 6)  # número não volta
                self.assertEqual([p.numero for p in loja.em_preparo()], [3, 4, 6])
                loja.arvore.validar()

    def test_consultas_do_gerente(self):
        for Arvore in ESTRUTURAS:
            with self.subTest(Arvore.nome):
                loja = loja_com_pedidos(Arvore, 10)  # cada pedido: R$ 25,00
                for _ in range(6):
                    loja.entregar_proximo()  # #1 a #6 entregues
                loja.cancelar(8)
                self.assertEqual(loja.pedido_seguinte(7).numero, 9)
                self.assertIsNone(loja.pedido_seguinte(10))
                self.assertEqual([p.numero for p in loja.pedidos_entre(5, 9)], [5, 6, 7, 9])
                self.assertEqual(loja.fechamento(1, 10), (6, 150.0))  # só entregues contam
                self.assertEqual(loja.fechamento(20, 30), (0, 0))

    def test_mesmo_resultado_nas_tres_arvores(self):
        resultados = []
        for Arvore in ESTRUTURAS:
            loja = Lanchonete.da_base(Arvore)
            resultados.append(
                (
                    len(loja),
                    loja.fechamento(1, 331),
                    loja.pedido_seguinte(11).numero,
                    [p.numero for p in loja.pedidos_entre(100, 150)],
                )
            )
        self.assertEqual(resultados[0], resultados[1])
        self.assertEqual(resultados[0], resultados[2])


class TestFormatacao(unittest.TestCase):
    def test_numeros_em_portugues(self):
        self.assertEqual(numero_br(2186), "2.186")
        self.assertEqual(numero_br(1093.5, 2), "1.093,50")
        self.assertEqual(reais(12529), "R$ 12.529,00")
        self.assertEqual(reais(7), "R$ 7,00")


class TestDemonstracao(unittest.TestCase):
    def test_main_roda_todas_as_partes(self):
        saida = io.StringIO()
        with redirect_stdout(saida):
            main.main([])
        texto = saida.getvalue()
        for parte in range(1, 6):
            self.assertIn(f"PARTE {parte}", texto)
        self.assertIn("caso direita-direita", texto)
        self.assertIn("remoção caso 4", texto)
        self.assertIn("pedido recusado: fora do cardápio: Pizza", texto)


if __name__ == "__main__":
    unittest.main()
