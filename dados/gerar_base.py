"""Gera dados/pedidos.csv: uma semana de pedidos simulados de uma lanchonete.

Roda com (na raiz do projeto): python -m dados.gerar_base

Regras da simulação (semente 42: rodar de novo gera o mesmo arquivo):
- 7 dias a partir de 16/11/2026, com a lanchonete aberta das 11:00 às 23:00;
- entre 250 e 350 pedidos por dia;
- o número do pedido é sequencial (1, 2, 3...) e acompanha o horário, como a
  senha do caixa. É por isso que os pedidos chegam na árvore EM ORDEM;
- cada pedido tem de 1 a 4 itens do cardápio, e o valor é a soma dos itens;
- cerca de 8% dos pedidos terminam cancelados.
"""

import csv
import random
from datetime import date, datetime, timedelta

from src.pedidos import CAMINHO_BASE, CAMPOS, CARDAPIO, FORMATO_DATA_HORA, SEPARADOR_ITENS

SEMENTE = 42
PRIMEIRO_DIA = date(2026, 11, 16)
DIAS = 7
ABERTURA, FECHAMENTO = 11, 23  # horas
PEDIDOS_POR_DIA = (250, 350)
CHANCE_CANCELAMENTO = 0.08

NOMES = [
    "Ana", "Bruno", "Carla", "Daniel", "Eduarda", "Felipe", "Gabriela", "Heitor",
    "Isabela", "João", "Larissa", "Lucas", "Mariana", "Nicolas", "Paula", "Rafael",
    "Sofia", "Thiago", "Vitória", "Yuri",
]
SOBRENOMES = [
    "Silva", "Souza", "Oliveira", "Santos", "Lima", "Costa", "Pereira", "Almeida",
    "Ferreira", "Rodrigues", "Gomes", "Martins",
]


def gerar_pedidos(semente=SEMENTE):
    """Devolve a lista de linhas (dicionários) da base, em ordem de chegada."""
    rng = random.Random(semente)
    pedidos, numero = [], 1
    for dia in range(DIAS):
        abertura = datetime.combine(PRIMEIRO_DIA + timedelta(days=dia), datetime.min.time())
        abertura += timedelta(hours=ABERTURA)
        minutos_abertos = (FECHAMENTO - ABERTURA) * 60
        quantidade = rng.randint(*PEDIDOS_POR_DIA)
        for minuto in sorted(rng.randrange(minutos_abertos) for _ in range(quantidade)):
            itens = rng.choices(list(CARDAPIO), k=rng.randint(1, 4))
            pedidos.append(
                {
                    "numero": numero,
                    "data_hora": (abertura + timedelta(minutes=minuto)).strftime(FORMATO_DATA_HORA),
                    "cliente": f"{rng.choice(NOMES)} {rng.choice(SOBRENOMES)}",
                    "itens": SEPARADOR_ITENS.join(itens),
                    "valor": f"{sum(CARDAPIO[item] for item in itens):.2f}",
                    "status": "cancelado" if rng.random() < CHANCE_CANCELAMENTO else "entregue",
                }
            )
            numero += 1
    return pedidos


def salvar(pedidos, caminho=CAMINHO_BASE):
    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS, lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(pedidos)


if __name__ == "__main__":
    pedidos = gerar_pedidos()
    salvar(pedidos)
    cancelados = sum(p["status"] == "cancelado" for p in pedidos)
    print(f"{len(pedidos)} pedidos gerados ({cancelados} cancelados) em {CAMINHO_BASE}")
