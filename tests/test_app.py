"""Testes do desenho em DOT e da interface Streamlit (sem abrir navegador)."""

import unittest
from pathlib import Path

from src.arvores import AVL, BST, ESTRUTURAS, RubroNegra
from src.visual import COR_PRETO, COR_VERMELHO, dot

try:
    from streamlit.testing.v1 import AppTest

    TEM_STREAMLIT = True
except ImportError:
    TEM_STREAMLIT = False

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def montar(Arvore, numeros):
    arvore = Arvore()
    for numero in numeros:
        arvore.inserir(numero)
    return arvore


class TestDesenhoDot(unittest.TestCase):
    def test_vazia_ou_grande_demais_nao_desenha(self):
        for Arvore in ESTRUTURAS:
            with self.subTest(Arvore.nome):
                self.assertIsNone(dot(Arvore()))
                self.assertIsNone(dot(montar(Arvore, range(1, 101)), max_nos=63))

    def test_um_no_e_uma_aresta_por_filho(self):
        for Arvore in ESTRUTURAS:
            with self.subTest(Arvore.nome):
                arvore = montar(Arvore, range(1, 8))
                texto = dot(arvore)
                for numero in range(1, 8):
                    self.assertIn(f"n{numero} [label=", texto)
                visiveis = [l for l in texto.splitlines() if " -> n" in l]
                self.assertEqual(len(visiveis), 6)  # 7 nós, 6 arestas

    def test_filho_unico_ganha_irmao_invisivel(self):
        """Na BST em escada, cada nó tem só o filho direito: o esquerdo vira um nó invisível."""
        texto = dot(montar(BST, [1, 2, 3]))
        self.assertIn("n1 -> vazio1 [style=invis];", texto)
        self.assertLess(texto.index("n1 -> vazio1"), texto.index("n1 -> n2"))  # esquerdo antes do direito

    def test_rotulos_e_cores(self):
        self.assertIn('label="#2\\nf=+0"', dot(montar(AVL, [1, 2, 3])))
        texto = dot(montar(RubroNegra, [1, 2, 3]))
        self.assertIn(f'n2 [label="#2", fillcolor="{COR_PRETO}"', texto)
        self.assertIn(f'n1 [label="#1", fillcolor="{COR_VERMELHO}"', texto)


@unittest.skipUnless(TEM_STREAMLIT, "streamlit não instalado")
class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(APP, default_timeout=120).run()

    def botao(self, inicio):
        return next(b for b in self.app.button if b.label.startswith(inicio))

    def test_abre_sem_erro(self):
        self.assertEqual(len(self.app.exception), 0)
        self.assertEqual([aba.label for aba in self.app.tabs], ["Caixa e cozinha", "Passo a passo", "Comparação"])

    def test_caixa_registra_entrega_e_recusa(self):
        self.app.text_input[0].input("Ana Lima")
        self.app.multiselect[0].select("X-Bacon").select("Refrigerante")
        self.botao("Registrar").click().run()
        self.assertEqual(self.app.success[0].value, "Pedido #2187 registrado: R$ 31,00")
        for loja in self.app.session_state.lojas.values():  # o pedido entrou nas três árvores
            self.assertIsNotNone(loja.consultar(2187))

        self.botao("Entregar").click().run()
        self.assertEqual(self.app.success[0].value, "Entregue: #2187 (Ana Lima)")

        self.app.number_input[0].set_value(5)
        self.botao("Cancelar (remoção)").click().run()
        self.assertIn("já foi entregue", self.app.error[0].value)
        self.assertEqual(len(self.app.exception), 0)

    def test_passo_a_passo_rotulo_acompanha_a_arvore(self):
        """Depois de 7 pedidos, o botão já diz #8 e um clique nele insere o #8."""
        self.botao("Chegaram 7").click().run()
        self.assertEqual(self.botao("Chegou o pedido").label, "Chegou o pedido #8")
        self.botao("Chegou o pedido").click().run()
        self.assertEqual(self.app.session_state.passo["arvore"].chaves(), list(range(1, 9)))
        self.assertTrue(self.app.code[0].value.startswith("pedido #8 chegou"))

        self.app.radio(key="arvore_passo").set_value("Rubro-Negra").run()
        self.assertEqual(len(self.app.session_state.passo["arvore"]), 0)  # trocar de árvore recomeça
        self.botao("Chegaram 7").click().run()
        self.assertIn("[Rubro-Negra] caso 3", self.app.code[0].value)
        self.assertEqual(len(self.app.exception), 0)


if __name__ == "__main__":
    unittest.main()
