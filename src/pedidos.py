"""Pedido da lanchonete e leitura da base (dados/pedidos.csv).

Na árvore, a chave é o número do pedido e o valor é o próprio Pedido.
"""

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

FORMATO_DATA_HORA = "%Y-%m-%d %H:%M"
SEPARADOR_ITENS = ";"
CAMINHO_BASE = Path(__file__).resolve().parent.parent / "dados" / "pedidos.csv"
CAMPOS = ["numero", "data_hora", "cliente", "itens", "valor", "status"]

CARDAPIO = {
    "X-Burguer": 18.00,
    "X-Salada": 20.00,
    "X-Bacon": 24.00,
    "X-Tudo": 29.00,
    "Cachorro-quente": 14.00,
    "Batata frita": 12.00,
    "Pastel": 9.00,
    "Refrigerante": 7.00,
    "Suco natural": 9.00,
    "Milk-shake": 16.00,
}


def numero_br(valor, casas=0):
    """12529.5 -> '12.529,50' (com casas=2): separadores do português."""
    return f"{valor:,.{casas}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def reais(valor):
    """12529.5 -> 'R$ 12.529,50'."""
    return f"R$ {numero_br(valor, 2)}"


@dataclass
class Pedido:
    numero: int  # chave da árvore: sequencial, como a senha do caixa
    data_hora: datetime
    cliente: str
    itens: list[str]
    valor: float
    status: str  # entregue ou cancelado

    def __str__(self):
        return (
            f"#{self.numero} | {self.data_hora:%d/%m %H:%M} | {self.cliente} | "
            f"{', '.join(self.itens)} | {reais(self.valor)}"
        )


def carregar_pedidos(caminho=CAMINHO_BASE):
    """Lê o CSV e devolve a lista de Pedido, na ordem do arquivo (ordem de chegada)."""
    with open(caminho, newline="", encoding="utf-8") as arquivo:
        return [
            Pedido(
                numero=int(linha["numero"]),
                data_hora=datetime.strptime(linha["data_hora"], FORMATO_DATA_HORA),
                cliente=linha["cliente"],
                itens=linha["itens"].split(SEPARADOR_ITENS),
                valor=float(linha["valor"]),
                status=linha["status"],
            )
            for linha in csv.DictReader(arquivo)
        ]
