"""Benchmark das árvores com os pedidos da lanchonete.

Roda com: python comparacao.py              (tamanhos padrão: 1.000 a 8.000 pedidos)
          python comparacao.py 500 1000     (tamanhos escolhidos)

Cenários (semente 42, as três árvores recebem exatamente as mesmas entradas):
- em_ordem:      pedidos chegando em ordem de número, como no caixa (pior caso da BST);
- embaralhado:   os mesmos números em ordem aleatória (caso médio da BST);
- cancelamentos: chegada em ordem e, depois, metade dos pedidos cancelada ao acaso;
- base_real:     os 2.186 pedidos de dados/pedidos.csv e os 165 cancelamentos.

Medidas que NÃO dependem da máquina (são sempre iguais para a mesma entrada):
altura, comparações por busca, rotações e recolorações.
Medidas que dependem da máquina: os tempos (mediana de 3 execuções, em ms).

Salva tudo em assets/resultados.json (lido por graficos.py).
"""

import json
import math
import platform
import random
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path

from src.arvores import ESTRUTURAS
from src.pedidos import carregar_pedidos, numero_br

SEMENTE = 42
TAMANHOS_PADRAO = [1000, 2000, 4000, 8000]
REPETICOES = 3
ARQUIVO_SAIDA = Path(__file__).resolve().parent / "assets" / "resultados.json"
CAMPOS_DE_TEMPO = ("tempo_insercao_ms", "tempo_busca_ms", "tempo_remocao_ms")


# ----------------------------------------------------------------------
# Cenários: cada um devolve (números inseridos, números removidos depois)
# ----------------------------------------------------------------------
def em_ordem(n):
    return list(range(1, n + 1)), []


def embaralhado(n):
    numeros = list(range(1, n + 1))
    random.Random(SEMENTE).shuffle(numeros)
    return numeros, []


def cancelamentos(n):
    numeros = list(range(1, n + 1))
    return numeros, random.Random(SEMENTE).sample(numeros, n // 2)


def base_real(_n=None):
    pedidos = carregar_pedidos()
    return [p.numero for p in pedidos], [p.numero for p in pedidos if p.status == "cancelado"]


CENARIOS = {
    "em_ordem": (em_ordem, "Pedidos em ordem de chegada"),
    "embaralhado": (embaralhado, "Pedidos em ordem aleatória"),
    "cancelamentos": (cancelamentos, "Chegada em ordem e metade cancelada"),
    "base_real": (base_real, "Base real: semana da lanchonete"),
}


def limites(n):
    """Alturas teóricas para n chaves (em níveis)."""
    return {
        "minima": math.floor(math.log2(n)) + 1,
        "avl": 1.4405 * math.log2(n + 2) - 0.3277,
        "rubro_negra": 2 * math.log2(n + 1),
    }


# ----------------------------------------------------------------------
# Medição
# ----------------------------------------------------------------------
def cronometrar(funcao, chaves):
    """Aplica a função em cada chave e devolve o tempo total em ms."""
    inicio = time.perf_counter()
    for chave in chaves:
        funcao(chave)
    return (time.perf_counter() - inicio) * 1000


def medir(Arvore, insercoes, remocoes, contar_buscas=True):
    """Uma rodada completa: insere tudo, busca tudo, remove os cancelados."""
    arvore = Arvore()
    medida = {"tempo_insercao_ms": cronometrar(arvore.inserir, insercoes)}
    medida["altura"] = arvore.altura()
    medida["rotacoes_insercao"] = arvore.rotacoes
    medida["recoloracoes_insercao"] = getattr(arvore, "recoloracoes", None)
    if contar_buscas:  # contagem determinística: basta fazer uma vez
        medida["comparacoes_por_busca"] = round(arvore.comparacoes_medias_busca(insercoes), 3)
    medida["tempo_busca_ms"] = cronometrar(arvore.buscar, insercoes)

    if remocoes:
        rotacoes, recoloracoes = arvore.rotacoes, getattr(arvore, "recoloracoes", None)
        medida["tempo_remocao_ms"] = cronometrar(arvore.remover, remocoes)
        medida["rotacoes_remocao"] = arvore.rotacoes - rotacoes
        medida["recoloracoes_remocao"] = None if recoloracoes is None else arvore.recoloracoes - recoloracoes
        medida["altura_apos_remocao"] = arvore.altura()

    arvore.validar()  # o número só vale se a árvore terminou correta
    return medida


def medir_com_repeticoes(Arvore, insercoes, remocoes, repeticoes):
    rodadas = [medir(Arvore, insercoes, remocoes, contar_buscas=(i == 0)) for i in range(repeticoes)]
    final = dict(rodadas[0])  # contagens são iguais em todas as rodadas
    for campo in CAMPOS_DE_TEMPO:
        if campo in final:
            final[campo] = round(statistics.median(r[campo] for r in rodadas), 3)
    return final


def imprimir(cenario, m):
    texto = (
        f"{cenario:<13} {m['estrutura']:<11} n={numero_br(m['n']):>5} | altura {numero_br(m['altura']):>5}"
        f" | busca {numero_br(m['comparacoes_por_busca'], 2):>8} comp."
        f" | inserção {numero_br(m['tempo_insercao_ms'], 1):>8} ms"
    )
    if "tempo_remocao_ms" in m:
        texto += f" | cancelamentos {numero_br(m['tempo_remocao_ms'], 1):>7} ms"
    print(texto, flush=True)


def main(tamanhos=None, caminho=ARQUIVO_SAIDA, repeticoes=REPETICOES):
    tamanhos = tamanhos or TAMANHOS_PADRAO
    resultados = {
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "python": platform.python_version(),
        "maquina": f"{platform.system()} {platform.machine()}",
        "repeticoes": repeticoes,
        "semente": SEMENTE,
        "estruturas": [Arvore.nome for Arvore in ESTRUTURAS],
        "tamanhos": tamanhos,
        "cenarios": {},
        "limites": {},
    }

    for nome, (gerar, descricao) in CENARIOS.items():
        linhas = []
        for n in [None] if nome == "base_real" else tamanhos:
            insercoes, remocoes = gerar(n)
            resultados["limites"][str(len(insercoes))] = limites(len(insercoes))
            for Arvore in ESTRUTURAS:
                medida = medir_com_repeticoes(Arvore, insercoes, remocoes, repeticoes)
                medida.update(estrutura=Arvore.nome, n=len(insercoes))
                linhas.append(medida)
                imprimir(nome, medida)
        resultados["cenarios"][nome] = {"descricao": descricao, "linhas": linhas}

    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(resultados, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nResultados salvos em {caminho}")
    return resultados


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main([int(t) for t in sys.argv[1:]])
