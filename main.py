"""Demonstração passo a passo das árvores na lanchonete.

Roda com: python main.py        (todas as partes)
          python main.py 3      (só a parte 3)

1. BST com pedidos em ordem: vira uma escada.
2. AVL e Rubro-Negra com os mesmos pedidos: cada rotação e recoloração.
3. Cancelamentos: remoção com rebalanceamento.
4. A semana inteira (base real) nas três árvores.
5. A lanchonete funcionando sobre a AVL.
"""

import math
import sys
from datetime import datetime

from src.arvores import AVL, BST, ESTRUTURAS, RubroNegra
from src.lanchonete import Lanchonete
from src.pedidos import carregar_pedidos, numero_br, reais

PEDIDOS_DEMO = list(range(1, 8))  # 7 pedidos chegando em ordem


def titulo(texto):
    print("\n" + "=" * 72)
    print(texto)
    print("=" * 72)


def resumo(arvore):
    texto = f"{arvore.nome} | pedidos: {len(arvore)} | altura: {arvore.altura()} | rotações: {arvore.rotacoes}"
    if hasattr(arvore, "recoloracoes"):
        texto += f" | recolorações: {arvore.recoloracoes}"
    return texto


def inserir_passo_a_passo(Arvore, numeros):
    arvore = Arvore(verbose=True)
    for numero in numeros:
        print(f"  pedido #{numero} chegou")
        arvore.inserir(numero)
    arvore.verbose = False
    return arvore


def parte_1():
    titulo("PARTE 1 - BST com os pedidos chegando em ordem")
    print("Cada pedido novo tem número maior que todos os anteriores,")
    print("então ele sempre vai para a DIREITA. A árvore vira uma escada.\n")
    arvore = inserir_passo_a_passo(BST, PEDIDOS_DEMO)
    print()
    print(arvore.desenhar())
    print()
    print(resumo(arvore))
    print(f"Altura = número de pedidos: achar o #{PEDIDOS_DEMO[-1]} custa {len(PEDIDOS_DEMO)} comparações.")


def parte_2():
    titulo("PARTE 2 - Os mesmos pedidos nas árvores balanceadas")
    for Arvore, legenda in ((AVL, "f = altura(esquerda) - altura(direita)"), (RubroNegra, "[V] vermelho  [P] preto")):
        print(f"\n--- {Arvore.nome} ---")
        arvore = inserir_passo_a_passo(Arvore, PEDIDOS_DEMO)
        print(f"\n({legenda})")
        print(arvore.desenhar())
        print()
        print(resumo(arvore))


def parte_3():
    titulo("PARTE 3 - Cancelamentos: remoção com rebalanceamento")
    print("Os 3 primeiros pedidos são cancelados. A BST só tira os degraus de baixo;")
    print("a AVL e a Rubro-Negra se reorganizam a cada remoção.")
    for Arvore in ESTRUTURAS:
        print(f"\n--- {Arvore.nome} ---")
        arvore = Arvore()
        for numero in PEDIDOS_DEMO:
            arvore.inserir(numero)
        arvore.zerar_contadores()
        arvore.verbose = True
        for numero in (1, 2, 3):
            print(f"  cancelar #{numero}")
            arvore.remover(numero)
        arvore.verbose = False
        print()
        print(arvore.desenhar())
        print()
        print(resumo(arvore) + " (só nas remoções)")


def parte_4():
    titulo("PARTE 4 - A semana inteira: 2.186 pedidos da base real")
    pedidos = carregar_pedidos()
    numeros = [pedido.numero for pedido in pedidos]
    cancelados = [pedido.numero for pedido in pedidos if pedido.status == "cancelado"]
    n = len(pedidos)
    print(f"{numero_br(n)} pedidos inseridos na ordem do arquivo (em ordem de número),"
          f" depois {len(cancelados)} cancelados.\n")
    print(f"Altura mínima possível: {math.floor(math.log2(n)) + 1}"
          f" | limite AVL: {numero_br(1.4405 * math.log2(n + 2) - 0.3277, 1)}"
          f" | limite Rubro-Negra: {numero_br(2 * math.log2(n + 1), 1)}\n")

    colunas = ["", *[Arvore.nome for Arvore in ESTRUTURAS]]
    linhas = {
        "altura": [],
        "comparações por busca (média)": [],
        "rotações": [],
        "recolorações": [],
        "altura depois dos cancelamentos": [],
    }
    for Arvore in ESTRUTURAS:
        arvore = Arvore()
        for pedido in pedidos:
            arvore.inserir(pedido.numero, pedido)
        linhas["altura"].append(numero_br(arvore.altura()))
        linhas["comparações por busca (média)"].append(numero_br(arvore.comparacoes_medias_busca(numeros), 2))
        for numero in cancelados:
            arvore.remover(numero)
        linhas["rotações"].append(numero_br(arvore.rotacoes))
        recoloracoes = getattr(arvore, "recoloracoes", None)
        linhas["recolorações"].append("-" if recoloracoes is None else numero_br(recoloracoes))
        linhas["altura depois dos cancelamentos"].append(numero_br(arvore.altura()))
        arvore.validar()

    largura = max(len(nome) for nome in linhas)
    print(f"{colunas[0]:<{largura}}" + "".join(f"{c:>14}" for c in colunas[1:]))
    print("-" * (largura + 14 * len(ESTRUTURAS)))
    for nome, valores in linhas.items():
        print(f"{nome:<{largura}}" + "".join(f"{v:>14}" for v in valores))
    print("\nNa BST, achar um pedido percorre em média metade da semana. Cancelar não conserta.")
    print("AVL e Rubro-Negra acham qualquer pedido com cerca de 11 comparações.")


def parte_5():
    titulo("PARTE 5 - A lanchonete funcionando (sobre a AVL)")
    loja = Lanchonete.da_base(AVL)
    print(f"Semana carregada: {len(loja)} pedidos no registro, próximo número: #{loja.proximo_numero}\n")

    print("Caixa (inserção):")
    hora = datetime(2026, 11, 23, 11, 0)
    for cliente, itens in (
        ("Ana Lima", ["X-Bacon", "Refrigerante"]),
        ("Bruno Costa", ["Pastel", "Pastel", "Suco natural"]),
        ("Carla Souza", ["X-Tudo", "Batata frita", "Milk-shake"]),
    ):
        print(f"  {loja.novo_pedido(cliente, itens, agora=hora)}")
    try:
        loja.novo_pedido("Daniel Gomes", ["Pizza"], agora=hora)
    except ValueError as erro:
        print(f"  pedido recusado: {erro}")

    print("\nPainel da cozinha (intervalo do último entregue até o último número):")
    for pedido in loja.em_preparo():
        print(f"  {pedido}")

    numero = loja.proximo_numero - 2
    print(f"\nConsultar #{numero} (busca): {loja.consultar(numero)}")
    print(f"Consultar #12 (busca): {loja.consultar(12) or 'não existe: foi cancelado na segunda-feira'}")

    print(f"\nCancelar #{numero} (remoção): {loja.cancelar(numero) is not None}")
    print(f"Cancelar #5 (já entregue): {loja.cancelar(5) or 'recusado'}")

    print(f"\nPróximo a preparar (sucessor de #{loja.ultimo_entregue}): {loja.proximo_a_preparar()}")
    print(f"Cozinha entregou: {loja.entregar_proximo()}")
    print("Painel da cozinha agora:")
    for pedido in loja.em_preparo():
        print(f"  {pedido}")

    print(f"\nPedido seguinte ao #11 (sucessor; o #12 foi cancelado): {loja.pedido_seguinte(11)}")
    quantidade, total = loja.fechamento(1, 331)
    print(f"Fechamento de segunda, 16/11, pedidos #1 a #331 (intervalo): {quantidade} entregues, {reais(total)}")


PARTES = [parte_1, parte_2, parte_3, parte_4, parte_5]


def main(argumentos):
    escolhidas = [int(a) for a in argumentos] or range(1, len(PARTES) + 1)
    for numero in escolhidas:
        PARTES[numero - 1]()
    print()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # desenho com "┌──" no terminal do Windows
    main(sys.argv[1:])
