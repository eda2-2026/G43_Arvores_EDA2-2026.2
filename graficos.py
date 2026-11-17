"""Gráficos do benchmark: lê assets/resultados.json e salva os PNGs em assets/.

Roda com: python graficos.py    (depois de python comparacao.py)
Precisa do matplotlib: pip install -r requirements.txt
"""

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # só gera arquivos, não abre janela
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from src.pedidos import numero_br

PASTA = Path(__file__).resolve().parent / "assets"

# Uma cor e um marcador fixos por árvore (paleta checada para daltonismo).
CORES = {"BST": "#2a78d6", "AVL": "#eb6834", "Rubro-Negra": "#1baf7a"}
MARCADORES = {"BST": "o", "AVL": "s", "Rubro-Negra": "^"}
FUNDO, TEXTO, TEXTO_SECUNDARIO, GRADE = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"

plt.rcParams.update(
    {
        "figure.facecolor": FUNDO,
        "axes.facecolor": FUNDO,
        "savefig.facecolor": FUNDO,
        "axes.edgecolor": GRADE,
        "axes.labelcolor": TEXTO_SECUNDARIO,
        "axes.titlecolor": TEXTO,
        "axes.titlesize": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,  # grade atrás das barras e linhas
        "grid.color": GRADE,
        "grid.linewidth": 0.8,
        "xtick.color": TEXTO_SECUNDARIO,
        "ytick.color": TEXTO_SECUNDARIO,
        "legend.frameon": False,
        "font.size": 10,
    }
)

FORMATO_BR = FuncFormatter(lambda valor, _: numero_br(valor, 0 if valor >= 10 or valor == int(valor) else 1))


def linhas_de(resultados, cenario, estrutura):
    return [l for l in resultados["cenarios"][cenario]["linhas"] if l["estrutura"] == estrutura]


def painel_de_linhas(ax, resultados, cenario, campo, titulo, log=False, limites=False):
    """Um painel com uma linha por árvore (x = número de pedidos)."""
    for estrutura in resultados["estruturas"]:
        linhas = linhas_de(resultados, cenario, estrutura)
        ax.plot(
            [l["n"] for l in linhas],
            [l[campo] for l in linhas],
            color=CORES[estrutura],
            marker=MARCADORES[estrutura],
            markersize=7,
            linewidth=2,
            label=estrutura,
        )
    if limites:
        tamanhos = resultados["tamanhos"]
        teoricos = [resultados["limites"][str(n)] for n in tamanhos]
        ax.plot(tamanhos, [t["rubro_negra"] for t in teoricos], color=TEXTO_SECUNDARIO,
                linestyle="--", linewidth=1.2, label="limite Rubro-Negra")
        ax.plot(tamanhos, [t["avl"] for t in teoricos], color=TEXTO_SECUNDARIO,
                linestyle="-.", linewidth=1.2, label="limite AVL")
        ax.plot(tamanhos, [t["minima"] for t in teoricos], color=TEXTO_SECUNDARIO,
                linestyle=":", linewidth=1.5, label="altura mínima")
    if log:
        ax.set_yscale("log")
    else:
        ax.set_ylim(bottom=0)
    ax.set_title(titulo)
    ax.set_xlabel("número de pedidos (n)")
    ax.xaxis.set_major_formatter(FORMATO_BR)
    ax.yaxis.set_major_formatter(FORMATO_BR)


def figura_de_dois_paineis(titulo):
    figura, eixos = plt.subplots(1, 2, figsize=(11, 4.2))
    figura.suptitle(titulo, color=TEXTO, fontsize=13, fontweight="bold")
    return figura, eixos


def legenda_no_topo(figura, ax):
    """Legenda numa linha só, logo abaixo do título: fora dos painéis, não cobre nenhum ponto."""
    handles, rotulos = ax.get_legend_handles_labels()
    figura.legend(handles, rotulos, loc="upper center", ncol=len(rotulos), bbox_to_anchor=(0.5, 0.925),
                  fontsize=9.5, handlelength=2.6)


def salvar(figura, pasta, nome):
    figura.tight_layout(rect=(0, 0, 1, 0.9 if figura.legends else 0.97))
    caminho = Path(pasta) / nome
    figura.savefig(caminho, dpi=130)
    plt.close(figura)
    print(f"  {caminho}")


def grafico_altura(resultados, pasta):
    figura, (esq, dir) = figura_de_dois_paineis("Altura da árvore (níveis)")
    painel_de_linhas(esq, resultados, "em_ordem", "altura", "Pedidos em ordem (escala log)", log=True, limites=True)
    painel_de_linhas(dir, resultados, "embaralhado", "altura", "Pedidos embaralhados", limites=True)
    esq.set_ylabel("altura (níveis)")
    legenda_no_topo(figura, esq)
    salvar(figura, pasta, "altura.png")


def grafico_comparacoes(resultados, pasta):
    figura, (esq, dir) = figura_de_dois_paineis("Comparações para achar um pedido (média)")
    painel_de_linhas(esq, resultados, "em_ordem", "comparacoes_por_busca", "Pedidos em ordem (escala log)", log=True)
    painel_de_linhas(dir, resultados, "embaralhado", "comparacoes_por_busca", "Pedidos embaralhados")
    esq.set_ylabel("comparações por busca")
    legenda_no_topo(figura, esq)
    salvar(figura, pasta, "comparacoes_busca.png")


def grafico_tempo_insercao(resultados, pasta):
    figura, (esq, dir) = figura_de_dois_paineis("Tempo para registrar todos os pedidos (ms)")
    painel_de_linhas(esq, resultados, "em_ordem", "tempo_insercao_ms", "Pedidos em ordem (escala log)", log=True)
    painel_de_linhas(dir, resultados, "embaralhado", "tempo_insercao_ms", "Pedidos embaralhados")
    esq.set_ylabel("tempo (ms)")
    legenda_no_topo(figura, esq)
    salvar(figura, pasta, "tempo_insercao.png")


def grafico_cancelamentos(resultados, pasta):
    figura, (esq, dir) = figura_de_dois_paineis("Cancelando metade dos pedidos (chegada em ordem)")
    painel_de_linhas(esq, resultados, "cancelamentos", "tempo_remocao_ms", "Tempo para cancelar (ms, escala log)", log=True)
    painel_de_linhas(dir, resultados, "cancelamentos", "altura_apos_remocao", "Altura depois (níveis, escala log)", log=True)
    legenda_no_topo(figura, esq)
    salvar(figura, pasta, "cancelamentos.png")


def barras(ax, rotulos, valores, cores, hachuras=None, formato=numero_br):
    posicoes = range(len(rotulos))
    barras_desenhadas = ax.bar(posicoes, valores, color=cores, width=0.62, edgecolor=FUNDO, linewidth=2,
                               hatch=hachuras)
    for barra, valor in zip(barras_desenhadas, valores):
        ax.annotate(formato(valor), (barra.get_x() + barra.get_width() / 2, barra.get_height()),
                    xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", color=TEXTO, fontsize=9)
    ax.set_xticks(list(posicoes), rotulos)
    ax.grid(axis="x", visible=False)
    ax.yaxis.set_major_formatter(FORMATO_BR)


def grafico_rebalanceamento(resultados, pasta):
    """Rotações por pedido (AVL e Rubro-Negra) e recolorações por pedido (Rubro-Negra), no maior n."""
    n = max(resultados["tamanhos"])
    figura, eixos = figura_de_dois_paineis(f"Trabalho de rebalanceamento por pedido registrado (n = {numero_br(n)})")
    for ax, cenario, titulo in zip(eixos, ("em_ordem", "embaralhado"), ("Pedidos em ordem", "Pedidos embaralhados")):
        avl = linhas_de(resultados, cenario, "AVL")[-1]
        rn = linhas_de(resultados, cenario, "Rubro-Negra")[-1]
        barras(
            ax,
            ["AVL\nrotações", "Rubro-Negra\nrotações", "Rubro-Negra\nrecolorações"],
            [avl["rotacoes_insercao"] / n, rn["rotacoes_insercao"] / n, rn["recoloracoes_insercao"] / n],
            [CORES["AVL"], CORES["Rubro-Negra"], CORES["Rubro-Negra"]],
            hachuras=["", "", "//"],
            formato=lambda v: numero_br(v, 2),
        )
        ax.set_title(titulo)
    eixos[0].set_ylabel("operações por pedido")
    salvar(figura, pasta, "rebalanceamento.png")


def grafico_base_real(resultados, pasta):
    linhas = resultados["cenarios"]["base_real"]["linhas"]
    n = linhas[0]["n"]
    nomes = [l["estrutura"] for l in linhas]
    cores = [CORES[nome] for nome in nomes]
    figura, (esq, dir) = figura_de_dois_paineis(f"Base real: a semana da lanchonete ({numero_br(n)} pedidos em ordem)")
    barras(esq, nomes, [l["altura"] for l in linhas], cores)
    esq.set_title("Altura (níveis, escala log)")
    barras(dir, nomes, [l["comparacoes_por_busca"] for l in linhas], cores, formato=lambda v: numero_br(v, 2))
    dir.set_title("Comparações por busca (média, escala log)")
    for ax in (esq, dir):
        ax.set_yscale("log")
        # barra em escala log começa em 1 (log 1 = 0); o topo deixa espaço para o rótulo
        ax.set_ylim(1, ax.get_ylim()[1] * 3)
        ax.yaxis.set_major_formatter(FORMATO_BR)
    salvar(figura, pasta, "base_real.png")


def main(caminho_json=PASTA / "resultados.json", pasta=PASTA):
    resultados = json.loads(Path(caminho_json).read_text(encoding="utf-8"))
    Path(pasta).mkdir(parents=True, exist_ok=True)
    print("Gráficos salvos:")
    for gerar in (grafico_altura, grafico_comparacoes, grafico_tempo_insercao,
                  grafico_cancelamentos, grafico_rebalanceamento, grafico_base_real):
        gerar(resultados, pasta)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
