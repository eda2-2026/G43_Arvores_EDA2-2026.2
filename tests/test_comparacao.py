"""Testes do benchmark (com tamanhos pequenos, para rodar rápido) e dos gráficos."""

import io
import json
import math
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import comparacao
from src.arvores import AVL, BST, ESTRUTURAS, RubroNegra

try:
    import matplotlib  # noqa: F401

    TEM_MATPLOTLIB = True
except ImportError:
    TEM_MATPLOTLIB = False


class TestMedicao(unittest.TestCase):
    def test_contagens_nao_dependem_da_rodada(self):
        insercoes, remocoes = comparacao.cancelamentos(300)
        for Arvore in ESTRUTURAS:
            with self.subTest(Arvore.nome):
                primeira = comparacao.medir(Arvore, insercoes, remocoes)
                segunda = comparacao.medir(Arvore, insercoes, remocoes)
                for campo in primeira:
                    if campo not in comparacao.CAMPOS_DE_TEMPO:
                        self.assertEqual(primeira[campo], segunda[campo], campo)

    def test_cenarios_usam_os_mesmos_numeros(self):
        for nome in ("em_ordem", "embaralhado", "cancelamentos"):
            gerar, _ = comparacao.CENARIOS[nome]
            insercoes, remocoes = gerar(100)
            self.assertEqual(sorted(insercoes), list(range(1, 101)))
            self.assertEqual(gerar(100), (insercoes, remocoes))  # semente fixa
            self.assertTrue(set(remocoes) <= set(insercoes))

    def test_valores_conhecidos_com_pedidos_em_ordem(self):
        n = 500
        insercoes, _ = comparacao.em_ordem(n)
        bst = comparacao.medir(BST, insercoes, [])
        self.assertEqual(bst["altura"], n)
        self.assertEqual(bst["comparacoes_por_busca"], (n + 1) / 2)
        self.assertIsNone(bst["recoloracoes_insercao"])
        avl = comparacao.medir(AVL, insercoes, [])
        self.assertEqual(avl["altura"], comparacao.limites(n)["minima"])
        rn = comparacao.medir(RubroNegra, insercoes, [])
        self.assertLessEqual(rn["altura"], comparacao.limites(n)["rubro_negra"])
        self.assertGreater(rn["recoloracoes_insercao"], 0)


class TestArquivoDeResultados(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pasta = tempfile.TemporaryDirectory()
        cls.caminho = Path(cls.pasta.name) / "resultados.json"
        with redirect_stdout(io.StringIO()):
            comparacao.main([100, 200], caminho=cls.caminho, repeticoes=1)
        cls.resultados = json.loads(cls.caminho.read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        cls.pasta.cleanup()

    def test_estrutura_do_json(self):
        r = self.resultados
        self.assertEqual(r["estruturas"], ["BST", "AVL", "Rubro-Negra"])
        self.assertEqual(set(r["cenarios"]), set(comparacao.CENARIOS))
        self.assertEqual(len(r["cenarios"]["em_ordem"]["linhas"]), 2 * 3)  # 2 tamanhos x 3 árvores
        self.assertEqual(len(r["cenarios"]["base_real"]["linhas"]), 3)
        self.assertEqual(r["cenarios"]["base_real"]["linhas"][0]["n"], 2186)
        for n in ("100", "200", "2186"):
            self.assertIn(n, r["limites"])
        self.assertEqual(r["limites"]["100"]["minima"], math.floor(math.log2(100)) + 1)

    def test_remocao_medida_so_quando_ha_cancelamentos(self):
        for linha in self.resultados["cenarios"]["embaralhado"]["linhas"]:
            self.assertNotIn("tempo_remocao_ms", linha)
        for linha in self.resultados["cenarios"]["cancelamentos"]["linhas"]:
            self.assertIn("altura_apos_remocao", linha)

    @unittest.skipUnless(TEM_MATPLOTLIB, "matplotlib não instalado")
    def test_graficos_sao_gerados(self):
        import graficos

        with redirect_stdout(io.StringIO()):
            graficos.main(self.caminho, self.pasta.name)
        for nome in ("altura", "comparacoes_busca", "tempo_insercao", "cancelamentos", "rebalanceamento", "base_real"):
            arquivo = Path(self.pasta.name) / f"{nome}.png"
            self.assertTrue(arquivo.exists() and arquivo.stat().st_size > 0, nome)


if __name__ == "__main__":
    unittest.main()
