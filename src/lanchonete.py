"""Regras da lanchonete em cima de uma árvore de busca.

A árvore é o registro de pedidos do caixa: chave = número do pedido, valor =
o Pedido. A estrutura (BST, AVL ou Rubro-Negra) é escolhida na criação, então
o mesmo código roda sobre as três.

Ciclo de um pedido:
- o caixa registra o pedido com o próximo número da sequência (inserção);
- a cozinha prepara em ordem de chegada e entrega (o status muda para
  "entregue"; o pedido continua no registro para consulta);
- um pedido ainda em preparo pode ser cancelado: ele sai do registro (remoção).

Como a cozinha entrega em ordem, vale sempre: todo pedido com número até
`ultimo_entregue` está entregue, e todo pedido acima dele está em preparo.
O próximo a preparar é, então, o SUCESSOR de `ultimo_entregue` na árvore.
Cancelados já saíram da árvore, então o sucessor pula por cima deles.
"""

from datetime import datetime

from .arvores import AVL
from .pedidos import CAMINHO_BASE, CARDAPIO, Pedido, carregar_pedidos

EM_PREPARO = "em preparo"
ENTREGUE = "entregue"
CANCELADO = "cancelado"


class Lanchonete:
    def __init__(self, Arvore=AVL):
        self.arvore = Arvore()
        self.proximo_numero = 1  # senha do caixa: nunca volta atrás, nem depois de cancelar
        self.ultimo_entregue = 0

    @classmethod
    def da_base(cls, Arvore=AVL, caminho=CAMINHO_BASE):
        """Reproduz a semana do CSV: registra todos os pedidos e depois cancela os cancelados."""
        lanchonete = cls(Arvore)
        pedidos = carregar_pedidos(caminho)
        for pedido in pedidos:
            lanchonete.arvore.inserir(pedido.numero, pedido)
        for pedido in pedidos:
            if pedido.status == CANCELADO:
                lanchonete.arvore.remover(pedido.numero)
        if pedidos:
            lanchonete.proximo_numero = pedidos[-1].numero + 1
            lanchonete.ultimo_entregue = pedidos[-1].numero  # a semana terminou com tudo entregue
        return lanchonete

    def __len__(self):
        return len(self.arvore)

    # ------------------------------------------------------------------
    # Caixa
    # ------------------------------------------------------------------
    def novo_pedido(self, cliente, itens, agora=None):
        """Inserção. Registra o pedido com o próximo número e calcula o valor pelo cardápio."""
        if not itens:
            raise ValueError("o pedido precisa de pelo menos um item")
        fora_do_cardapio = [item for item in itens if item not in CARDAPIO]
        if fora_do_cardapio:
            raise ValueError(f"fora do cardápio: {', '.join(fora_do_cardapio)}")
        pedido = Pedido(
            numero=self.proximo_numero,
            data_hora=agora or datetime.now().replace(second=0, microsecond=0),
            cliente=cliente,
            itens=list(itens),
            valor=sum(CARDAPIO[item] for item in itens),
            status=EM_PREPARO,
        )
        self.arvore.inserir(pedido.numero, pedido)
        self.proximo_numero += 1
        return pedido

    def consultar(self, numero):
        """Busca. Devolve o pedido, ou None se ele não existe (ou foi cancelado)."""
        return self.arvore.buscar(numero)

    def cancelar(self, numero):
        """Remoção. Só pedido em preparo pode ser cancelado. Devolve o pedido, ou None."""
        pedido = self.arvore.buscar(numero)
        if pedido is None or pedido.status != EM_PREPARO:
            return None
        self.arvore.remover(numero)
        pedido.status = CANCELADO
        return pedido

    # ------------------------------------------------------------------
    # Cozinha
    # ------------------------------------------------------------------
    def proximo_a_preparar(self):
        """Sucessor do último entregue: o pedido em preparo mais antigo, ou None."""
        numero = self.arvore.sucessor(self.ultimo_entregue)
        return None if numero is None else self.arvore.buscar(numero)

    def entregar_proximo(self):
        """A cozinha entrega o pedido em preparo mais antigo. Devolve ele, ou None."""
        pedido = self.proximo_a_preparar()
        if pedido is not None:
            pedido.status = ENTREGUE
            self.ultimo_entregue = pedido.numero
        return pedido

    def em_preparo(self):
        """Busca por intervalo: o painel da cozinha, do mais antigo ao mais novo."""
        return self.pedidos_entre(self.ultimo_entregue + 1, self.proximo_numero - 1)

    # ------------------------------------------------------------------
    # Consultas do gerente
    # ------------------------------------------------------------------
    def pedido_seguinte(self, numero):
        """Sucessor: o pedido registrado logo depois de `numero` (cancelados não contam)."""
        seguinte = self.arvore.sucessor(numero)
        return None if seguinte is None else self.arvore.buscar(seguinte)

    def pedidos_entre(self, inicio, fim):
        """Busca por intervalo: pedidos do #inicio ao #fim, em ordem."""
        return [pedido for _, pedido in self.arvore.intervalo(inicio, fim)]

    def fechamento(self, inicio, fim):
        """Fechamento de caixa do #inicio ao #fim: (quantidade entregue, total vendido)."""
        entregues = [p for p in self.pedidos_entre(inicio, fim) if p.status == ENTREGUE]
        return len(entregues), round(sum(p.valor for p in entregues), 2)
