"""Desenho das árvores em DOT (Graphviz), usado pela interface Streamlit.

O Graphviz não sabe o que é filho esquerdo ou direito: com um filho só, ele
centraliza. Para a árvore sair com a forma certa, todo nó com um filho ganha
um nó invisível no lugar do filho que falta.
"""

from .arvores.rubro_negra import VERMELHO

COR_BORDA = "#52514e"
COR_PADRAO = "#f3f2ee"  # BST e AVL: nó claro, texto escuro
COR_VERMELHO, COR_PRETO = "#d03b3b", "#1f1f1f"  # Rubro-Negra: as cores da própria regra


def _estilo(arvore, no):
    """Rótulo e cores de um nó, conforme a árvore."""
    if hasattr(no, "altura"):  # AVL: mostra o fator
        fator = (no.esq.altura if no.esq else 0) - (no.dir.altura if no.dir else 0)
        return f"#{no.chave}\\nf={fator:+d}", COR_PADRAO, "#0b0b0b"
    if hasattr(no, "cor"):  # Rubro-Negra: pinta o nó
        return f"#{no.chave}", COR_VERMELHO if no.cor == VERMELHO else COR_PRETO, "#ffffff"
    return f"#{no.chave}", COR_PADRAO, "#0b0b0b"


def dot(arvore, max_nos=63):
    """Texto DOT da árvore, ou None se ela está vazia ou é grande demais para desenhar."""
    nil = arvore._nil
    if arvore.raiz is nil or len(arvore) > max_nos:
        return None

    linhas = [
        "digraph arvore {",
        '  graph [bgcolor="transparent", nodesep=0.25, ranksep=0.35, ordering=out];  // esquerdo antes do direito',
        f'  node [shape=circle, style=filled, fontname="Helvetica", fontsize=11, width=0.55, fixedsize=true, color="{COR_BORDA}"];',
        f'  edge [color="{COR_BORDA}", arrowhead=none];',
    ]
    pilha, vazios = [arvore.raiz], 0
    while pilha:
        no = pilha.pop()
        rotulo, fundo, texto = _estilo(arvore, no)
        linhas.append(f'  n{no.chave} [label="{rotulo}", fillcolor="{fundo}", fontcolor="{texto}"];')
        filhos = [no.esq, no.dir]
        if all(filho is nil for filho in filhos):
            continue
        for filho in filhos:
            if filho is nil:  # segura o lugar do filho que falta
                vazios += 1
                linhas.append(f"  vazio{vazios} [style=invis];")
                linhas.append(f"  n{no.chave} -> vazio{vazios} [style=invis];")
            else:
                linhas.append(f"  n{no.chave} -> n{filho.chave};")
                pilha.append(filho)
    linhas.append("}")
    return "\n".join(linhas)
