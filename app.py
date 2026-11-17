"""Interface da Lanchonete em Árvores.

Roda com: streamlit run app.py

- Caixa e cozinha: a lanchonete funcionando, com cada operação rodando nas três
  árvores ao mesmo tempo (mesmos pedidos), para comparar o custo de cada uma.
- Passo a passo: uma árvore pequena, montada pedido a pedido, com o desenho e
  cada rotação e recoloração.
- Comparação: a semana inteira nas três árvores e os gráficos do benchmark.
"""

import io
from contextlib import redirect_stdout
from pathlib import Path

import streamlit as st

from src.arvores import ESTRUTURAS
from src.lanchonete import Lanchonete
from src.pedidos import CARDAPIO, numero_br, reais
from src.visual import dot

PASTA_ASSETS = Path(__file__).resolve().parent / "assets"
ARVORES = {Arvore.nome: Arvore for Arvore in ESTRUTURAS}

# Ocupar a largura toda: o Streamlit 1.50+ usa width="stretch"; versões
# anteriores (testado na 1.40) só aceitam use_container_width=True.
_VERSAO = tuple(int(parte) for parte in st.__version__.split(".")[:2])
LARGURA_TOTAL = {"width": "stretch"} if _VERSAO >= (1, 50) else {"use_container_width": True}

st.set_page_config(page_title="Lanchonete em Árvores", page_icon="🍔", layout="wide")


# ----------------------------------------------------------------------
# Estado da sessão
# ----------------------------------------------------------------------
def iniciar_estado():
    if "lojas" not in st.session_state:
        st.session_state.lojas = {nome: Lanchonete.da_base(Arvore) for nome, Arvore in ARVORES.items()}
        st.session_state.ultima = None  # (descrição, {árvore: comparações})
    if "passo" not in st.session_state:
        reiniciar_passo_a_passo("AVL")


def reiniciar_passo_a_passo(nome):
    st.session_state.passo = {"nome": nome, "arvore": ARVORES[nome](verbose=True), "log": ""}


def em_todas(descricao, operacao):
    """Roda a mesma operação nas três lojas e guarda quantas comparações cada árvore fez."""
    resultados, comparacoes = {}, {}
    for nome, loja in st.session_state.lojas.items():
        antes = loja.arvore.comparacoes
        resultados[nome] = operacao(loja)
        comparacoes[nome] = loja.arvore.comparacoes - antes
    st.session_state.ultima = (descricao, comparacoes)
    return resultados["AVL"]  # as três dão o mesmo resultado; a AVL representa


def linha(pedido):
    return {
        "Nº": pedido.numero,
        "Horário": f"{pedido.data_hora:%d/%m %H:%M}",
        "Cliente": pedido.cliente,
        "Itens": ", ".join(pedido.itens),
        "Valor": reais(pedido.valor),
        "Status": pedido.status,
    }


def metricas(arvore, comparacoes=None):
    st.metric("Altura (níveis)", numero_br(arvore.altura()))
    if comparacoes is not None:
        st.metric("Comparações na última operação", numero_br(comparacoes))
    st.metric("Rotações (total)", numero_br(arvore.rotacoes))
    if hasattr(arvore, "recoloracoes"):
        st.metric("Recolorações (total)", numero_br(arvore.recoloracoes))


# ----------------------------------------------------------------------
# Aba 1: caixa e cozinha
# ----------------------------------------------------------------------
def aba_caixa():
    lojas = st.session_state.lojas
    avl = lojas["AVL"]
    st.caption(
        f"O registro começa com a semana da base real ({numero_br(len(avl))} pedidos). "
        "Cada operação roda nas três árvores, com os mesmos pedidos."
    )

    caixa, operacoes = st.columns(2)
    with caixa:
        st.subheader("Caixa")
        with st.form("novo_pedido", clear_on_submit=True):
            cliente = st.text_input("Cliente")
            itens = st.multiselect(
                "Itens", list(CARDAPIO), format_func=lambda item: f"{item} ({reais(CARDAPIO[item])})"
            )
            if st.form_submit_button("Registrar pedido (inserção)", type="primary"):
                if not cliente.strip() or not itens:
                    st.error("Informe o cliente e pelo menos um item.")
                else:
                    pedido = em_todas("registrar pedido", lambda loja: loja.novo_pedido(cliente.strip(), itens))
                    st.success(f"Pedido #{pedido.numero} registrado: {reais(pedido.valor)}")

    with operacoes:
        st.subheader("Pedido")
        numero = st.number_input("Número do pedido", min_value=1, step=1, value=152)
        consultar, cancelar, entregar = st.columns(3)
        if consultar.button("Consultar (busca)", **LARGURA_TOTAL):
            pedido = em_todas(f"consultar #{numero}", lambda loja: loja.consultar(numero))
            st.info(str(pedido) + f" | {pedido.status}" if pedido else f"O pedido #{numero} não existe ou foi cancelado.")
        if cancelar.button("Cancelar (remoção)", **LARGURA_TOTAL):
            pedido = em_todas(f"cancelar #{numero}", lambda loja: loja.cancelar(numero))
            if pedido:
                st.warning(f"Pedido #{numero} cancelado.")
            else:
                st.error(f"Não dá para cancelar o #{numero}: não existe ou já foi entregue.")
        if entregar.button("Entregar próximo (sucessor)", **LARGURA_TOTAL):
            pedido = em_todas("entregar o próximo", lambda loja: loja.entregar_proximo())
            st.success(f"Entregue: #{pedido.numero} ({pedido.cliente})" if pedido else "Nenhum pedido em preparo.")

    st.divider()
    ultima = st.session_state.ultima
    st.subheader("Custo nas três árvores" + (f": {ultima[0]}" if ultima else ""))
    for coluna, (nome, loja) in zip(st.columns(3), lojas.items()):
        with coluna:
            st.markdown(f"**{nome}**")
            metricas(loja.arvore, ultima[1][nome] if ultima else None)

    st.divider()
    painel, fechamento = st.columns([3, 2])
    with painel:
        st.subheader("Painel da cozinha (intervalo)")
        em_preparo = avl.em_preparo()
        if em_preparo:
            st.dataframe([linha(p) for p in em_preparo], hide_index=True, **LARGURA_TOTAL)
        else:
            st.caption("Nenhum pedido em preparo. Registre um no caixa.")
    with fechamento:
        st.subheader("Fechamento de caixa (intervalo)")
        inicio, fim = st.columns(2)
        de = inicio.number_input("Do pedido", min_value=1, value=1, step=1)
        ate = fim.number_input("Até o pedido", min_value=1, value=331, step=1)
        quantidade, total = avl.fechamento(de, ate)
        st.metric(f"Entregues do #{de} ao #{ate}", f"{numero_br(quantidade)} pedidos", reais(total), delta_color="off")


# ----------------------------------------------------------------------
# Aba 2: passo a passo
# ----------------------------------------------------------------------
def executar_passo(descricao, operacao):
    passo = st.session_state.passo
    saida = io.StringIO()
    with redirect_stdout(saida):
        operacao(passo["arvore"])
    passo["log"] = descricao + "\n" + (saida.getvalue() or "    (nenhum rebalanceamento)")


# As ações rodam em callbacks (on_click), ANTES de a tela ser montada de novo:
# assim o rótulo "Chegou o pedido #N" já sai com o número certo, e as chaves
# fixas (key=...) fazem o clique valer mesmo quando o rótulo muda.
def proximo_numero():
    return (st.session_state.passo["arvore"].maximo() or 0) + 1


def chegar(quantidade):
    inicio = proximo_numero()
    fim = inicio + quantidade - 1
    descricao = f"pedido #{inicio} chegou" if quantidade == 1 else f"pedidos #{inicio} a #{fim} chegaram"
    executar_passo(descricao, lambda a: [a.inserir(n) for n in range(inicio, fim + 1)])


def cancelar_no_passo():
    numero = st.session_state.numero_passo
    executar_passo(f"cancelar #{numero}", lambda a: a.remover(numero))


def aba_passo_a_passo():
    nomes = list(ARVORES)
    nome = st.radio(
        "Árvore", nomes, index=nomes.index(st.session_state.passo["nome"]), horizontal=True, key="arvore_passo",
        on_change=lambda: reiniciar_passo_a_passo(st.session_state.arvore_passo),
    )
    b1, b2, b3, b4, b5 = st.columns([2, 2, 1.4, 1.4, 1.2])
    b1.button(f"Chegou o pedido #{proximo_numero()}", type="primary", **LARGURA_TOTAL, key="chegou_um",
              on_click=chegar, args=(1,))
    b2.button("Chegaram 7 pedidos em ordem", **LARGURA_TOTAL, key="chegaram_sete", on_click=chegar, args=(7,))
    numero = b3.number_input("Número", min_value=1, step=1, value=1, label_visibility="collapsed", key="numero_passo")
    b4.button(f"Cancelar #{numero}", **LARGURA_TOTAL, key="cancelar_passo", on_click=cancelar_no_passo)
    b5.button("Recomeçar", **LARGURA_TOTAL, key="recomecar", on_click=lambda: reiniciar_passo_a_passo(nome))
    arvore = st.session_state.passo["arvore"]

    desenho, lado = st.columns([3, 1])
    with desenho:
        texto = dot(arvore)
        if texto:
            st.graphviz_chart(texto)
        elif len(arvore) == 0:
            st.info("Árvore vazia. Clique em \"Chegou o pedido #1\".")
        else:
            st.info(f"{numero_br(len(arvore))} pedidos: grande demais para desenhar. Clique em Recomeçar.")
        legendas = {
            "AVL": "f = altura(esquerda) − altura(direita); a regra é f entre −1 e +1.",
            "Rubro-Negra": "Nó vermelho não tem filho vermelho; todo caminho tem a mesma quantidade de pretos.",
            "BST": "Sem balanceamento: pedidos em ordem viram uma escada.",
        }
        st.caption(legendas[nome])
    with lado:
        metricas(arvore)
    if st.session_state.passo["log"]:
        st.code(st.session_state.passo["log"], language=None)


# ----------------------------------------------------------------------
# Aba 3: comparação
# ----------------------------------------------------------------------
def aba_comparacao():
    lojas = st.session_state.lojas
    st.caption("O registro atual (a semana da base real e o que foi feito no caixa) nas três árvores.")
    tabela = []
    for nome, loja in lojas.items():
        amostra = loja.arvore.chaves()[::10]  # 1 em cada 10 pedidos: média quase exata e rápida
        tabela.append(
            {
                "Árvore": nome,
                "Pedidos": numero_br(len(loja)),
                "Altura (níveis)": numero_br(loja.arvore.altura()),
                "Comparações por busca (média)": numero_br(loja.arvore.comparacoes_medias_busca(amostra), 2),
                "Rotações": numero_br(loja.arvore.rotacoes),
                "Recolorações": numero_br(getattr(loja.arvore, "recoloracoes", 0)) if nome == "Rubro-Negra" else "-",
            }
        )
    st.dataframe(tabela, hide_index=True, **LARGURA_TOTAL)

    graficos = [
        ("altura.png", "Altura: com pedidos em ordem, a BST vira lista; a AVL fica na altura mínima."),
        ("comparacoes_busca.png", "Comparações para achar um pedido."),
        ("tempo_insercao.png", "Tempo para registrar todos os pedidos."),
        ("cancelamentos.png", "Cancelando metade dos pedidos."),
        ("rebalanceamento.png", "Rotações e recolorações por pedido registrado."),
        ("base_real.png", "A semana da lanchonete nas três árvores."),
    ]
    existentes = [(PASTA_ASSETS / arquivo, legenda) for arquivo, legenda in graficos if (PASTA_ASSETS / arquivo).exists()]
    if not existentes:
        st.info("Rode `python comparacao.py` e `python graficos.py` para gerar os gráficos do benchmark.")
    for i in range(0, len(existentes), 2):
        for coluna, (caminho, legenda) in zip(st.columns(2), existentes[i : i + 2]):
            coluna.image(str(caminho), caption=legenda, **LARGURA_TOTAL)


# ----------------------------------------------------------------------
iniciar_estado()
st.title("🍔 Lanchonete em Árvores")
st.caption("BST, AVL e Rubro-Negra guardando os pedidos de uma lanchonete. Chave = número do pedido.")
caixa, passo_a_passo, comparacao = st.tabs(["Caixa e cozinha", "Passo a passo", "Comparação"])
with caixa:
    aba_caixa()
with passo_a_passo:
    aba_passo_a_passo()
with comparacao:
    aba_comparacao()
