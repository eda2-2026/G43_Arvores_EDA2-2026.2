"""Árvore Rubro-Negra (Cormen et al., Introduction to Algorithms, cap. 13).

É uma BST em que cada nó é vermelho ou preto, com 5 regras:

    1. todo nó é vermelho ou preto;
    2. a raiz é preta;
    3. toda folha vazia (sentinela) é preta;
    4. nó vermelho não tem filho vermelho;
    5. todo caminho de um nó até as folhas vazias tem a mesma quantidade de
       nós pretos (a "altura preta").

Juntas, elas limitam a altura a 2 * log2(n + 1), então busca, inserção e
remoção custam O(log n). As regras são mais folgadas que as da AVL: a árvore
fica um pouco mais alta, mas rebalanceia com menos rotações, trocando cores.

Todas as folhas vazias e o pai da raiz são o MESMO nó sentinela preto
(`self._nil`). Assim todo nó tem pai e filhos de verdade, com cor, e o código
não precisa testar None a cada passo.

Inserção (o nó novo entra vermelho; o problema é pai vermelho):
    caso 1: tio vermelho              -> recolore pai, tio e avô; sobe para o avô
    caso 2: tio preto, nó em "joelho" -> rotação no pai; vira o caso 3
    caso 3: tio preto, em linha reta  -> recolore e rotação no avô; fim
No máximo 2 rotações por inserção.

Remoção (se sai um nó preto, um caminho fica com um preto a menos: o "duplo
preto"), olhando o irmão do nó que ficou com o duplo preto:
    caso 1: irmão vermelho                         -> rotação no pai; vira 2, 3 ou 4
    caso 2: irmão preto com os dois filhos pretos  -> irmão fica vermelho; sobe para o pai
    caso 3: irmão preto, sobrinho de perto vermelho -> rotação no irmão; vira o caso 4
    caso 4: irmão preto, sobrinho de longe vermelho -> recolore e rotação no pai; fim
No máximo 3 rotações por remoção.

Cada caso tem a versão espelhada (esquerda <-> direita), escrita por extenso
como no livro.
"""

from .base import ArvoreBusca, No

VERMELHO = "vermelho"
PRETO = "preto"


class NoRN(No):
    __slots__ = ("cor", "pai")

    def __init__(self, chave, valor=None, nil=None):
        super().__init__(chave, valor, nil=nil)
        self.pai = nil
        self.cor = VERMELHO  # todo nó novo entra vermelho


class RubroNegra(ArvoreBusca):
    nome = "Rubro-Negra"

    def __init__(self, verbose=False):
        super().__init__(verbose=verbose)
        self.recoloracoes = 0

    def _criar_nil(self):
        nil = NoRN(None)
        nil.cor = PRETO
        nil.esq = nil.dir = nil.pai = nil
        return nil

    def zerar_contadores(self):
        super().zerar_contadores()
        self.recoloracoes = 0

    def _pintar(self, no, cor):
        """Troca a cor de um nó de verdade. Só conta como recoloração se a cor mudou."""
        if no is not self._nil and no.cor != cor:
            no.cor = cor
            self.recoloracoes += 1

    def _nome(self, no):
        return "folha vazia" if no is self._nil else f"#{no.chave}"

    # ------------------------------------------------------------------
    # Rotações (mesma ideia da AVL, mas acertando também o ponteiro para o pai)
    # ------------------------------------------------------------------
    def _rotacao_esquerda(self, x):
        y = x.dir
        x.dir = y.esq
        if y.esq is not self._nil:
            y.esq.pai = x
        self._trocar_filho(x.pai, x, y)
        y.esq = x
        x.pai = y
        self.rotacoes += 1
        self._log(f"rotação à esquerda em #{x.chave} (#{y.chave} sobe)")

    def _rotacao_direita(self, y):
        x = y.esq
        y.esq = x.dir
        if x.dir is not self._nil:
            x.dir.pai = y
        self._trocar_filho(y.pai, y, x)
        x.dir = y
        y.pai = x
        self.rotacoes += 1
        self._log(f"rotação à direita em #{y.chave} (#{x.chave} sobe)")

    def _trocar_filho(self, pai, antigo, novo):
        """Coloca `novo` no lugar de `antigo` como filho de `pai` (ou como raiz)."""
        if pai is self._nil:
            self.raiz = novo
        elif antigo is pai.esq:
            pai.esq = novo
        else:
            pai.dir = novo
        novo.pai = pai

    # ------------------------------------------------------------------
    # Inserção
    # ------------------------------------------------------------------
    def inserir(self, chave, valor=None):
        pai, atual = self._nil, self.raiz
        while atual is not self._nil:
            self.comparacoes += 1
            if chave == atual.chave:
                return False  # número de pedido já existe
            pai = atual
            atual = atual.esq if chave < atual.chave else atual.dir

        novo = NoRN(chave, valor, nil=self._nil)
        novo.pai = pai
        if pai is self._nil:
            self.raiz = novo
        elif chave < pai.chave:
            pai.esq = novo
        else:
            pai.dir = novo
        self.tamanho += 1
        self._corrigir_insercao(novo)
        return True

    def _corrigir_insercao(self, z):
        while z.pai.cor == VERMELHO:  # regra 4 quebrada: z e o pai são vermelhos
            avo = z.pai.pai  # existe: um pai vermelho não pode ser a raiz
            if z.pai is avo.esq:
                tio = avo.dir
                if tio.cor == VERMELHO:
                    self._log(f"caso 1 em #{z.chave}: tio #{tio.chave} vermelho -> recolore e sobe para o avô #{avo.chave}")
                    self._pintar(z.pai, PRETO)
                    self._pintar(tio, PRETO)
                    self._pintar(avo, VERMELHO)
                    z = avo
                else:
                    if z is z.pai.dir:
                        self._log(f"caso 2 em #{z.chave}: tio preto e nó em joelho -> rotação no pai #{z.pai.chave}")
                        z = z.pai
                        self._rotacao_esquerda(z)
                    self._log(f"caso 3 em #{z.chave}: tio preto em linha reta -> recolore e rotação no avô #{avo.chave}")
                    self._pintar(z.pai, PRETO)
                    self._pintar(avo, VERMELHO)
                    self._rotacao_direita(avo)
            else:  # espelho: o pai é filho direito do avô
                tio = avo.esq
                if tio.cor == VERMELHO:
                    self._log(f"caso 1 em #{z.chave}: tio #{tio.chave} vermelho -> recolore e sobe para o avô #{avo.chave}")
                    self._pintar(z.pai, PRETO)
                    self._pintar(tio, PRETO)
                    self._pintar(avo, VERMELHO)
                    z = avo
                else:
                    if z is z.pai.esq:
                        self._log(f"caso 2 em #{z.chave}: tio preto e nó em joelho -> rotação no pai #{z.pai.chave}")
                        z = z.pai
                        self._rotacao_direita(z)
                    self._log(f"caso 3 em #{z.chave}: tio preto em linha reta -> recolore e rotação no avô #{avo.chave}")
                    self._pintar(z.pai, PRETO)
                    self._pintar(avo, VERMELHO)
                    self._rotacao_esquerda(avo)
        self._pintar(self.raiz, PRETO)  # regra 2

    # ------------------------------------------------------------------
    # Remoção
    # ------------------------------------------------------------------
    def remover(self, chave):
        z = self._buscar_no(chave)
        if z is self._nil:
            return False

        # y é o nó que sai de fato da sua posição; x é quem ocupa o lugar de y
        y, cor_que_saiu = z, z.cor
        if z.esq is self._nil:
            x = z.dir
            self._trocar_filho(z.pai, z, z.dir)
        elif z.dir is self._nil:
            x = z.esq
            self._trocar_filho(z.pai, z, z.esq)
        else:
            # dois filhos: o sucessor y (menor da direita) toma o lugar de z
            y = self._minimo_no(z.dir)
            cor_que_saiu = y.cor
            x = y.dir
            if y.pai is z:
                x.pai = y  # x pode ser a sentinela: o pai provisório é usado na correção
            else:
                self._trocar_filho(y.pai, y, y.dir)
                y.dir = z.dir
                y.dir.pai = y
            self._trocar_filho(z.pai, z, y)
            y.esq = z.esq
            y.esq.pai = y
            self._pintar(y, z.cor)  # y herda a cor de quem ele substituiu

        self.tamanho -= 1
        if cor_que_saiu == PRETO:
            self._log(f"saiu um nó preto: {self._nome(x)} fica com um preto a menos (duplo preto)")
            self._corrigir_remocao(x)
        self._nil.pai = self._nil  # devolve a sentinela ao estado normal
        return True

    def _corrigir_remocao(self, x):
        while x is not self.raiz and x.cor == PRETO:
            if x is x.pai.esq:
                irmao = x.pai.dir
                if irmao.cor == VERMELHO:
                    self._log(f"remoção caso 1: irmão #{irmao.chave} vermelho -> recolore e rotação no pai #{x.pai.chave}")
                    self._pintar(irmao, PRETO)
                    self._pintar(x.pai, VERMELHO)
                    self._rotacao_esquerda(x.pai)
                    irmao = x.pai.dir
                if irmao.esq.cor == PRETO and irmao.dir.cor == PRETO:
                    self._log(f"remoção caso 2: irmão #{irmao.chave} com filhos pretos -> fica vermelho; sobe para #{x.pai.chave}")
                    self._pintar(irmao, VERMELHO)
                    x = x.pai
                else:
                    if irmao.dir.cor == PRETO:
                        self._log(f"remoção caso 3: sobrinho de perto #{irmao.esq.chave} vermelho -> rotação no irmão #{irmao.chave}")
                        self._pintar(irmao.esq, PRETO)
                        self._pintar(irmao, VERMELHO)
                        self._rotacao_direita(irmao)
                        irmao = x.pai.dir
                    self._log(f"remoção caso 4: sobrinho de longe #{irmao.dir.chave} vermelho -> rotação no pai #{x.pai.chave}")
                    self._pintar(irmao, x.pai.cor)
                    self._pintar(x.pai, PRETO)
                    self._pintar(irmao.dir, PRETO)
                    self._rotacao_esquerda(x.pai)
                    x = self.raiz
            else:  # espelho: x é filho direito
                irmao = x.pai.esq
                if irmao.cor == VERMELHO:
                    self._log(f"remoção caso 1: irmão #{irmao.chave} vermelho -> recolore e rotação no pai #{x.pai.chave}")
                    self._pintar(irmao, PRETO)
                    self._pintar(x.pai, VERMELHO)
                    self._rotacao_direita(x.pai)
                    irmao = x.pai.esq
                if irmao.dir.cor == PRETO and irmao.esq.cor == PRETO:
                    self._log(f"remoção caso 2: irmão #{irmao.chave} com filhos pretos -> fica vermelho; sobe para #{x.pai.chave}")
                    self._pintar(irmao, VERMELHO)
                    x = x.pai
                else:
                    if irmao.esq.cor == PRETO:
                        self._log(f"remoção caso 3: sobrinho de perto #{irmao.dir.chave} vermelho -> rotação no irmão #{irmao.chave}")
                        self._pintar(irmao.dir, PRETO)
                        self._pintar(irmao, VERMELHO)
                        self._rotacao_esquerda(irmao)
                        irmao = x.pai.esq
                    self._log(f"remoção caso 4: sobrinho de longe #{irmao.esq.chave} vermelho -> rotação no pai #{x.pai.chave}")
                    self._pintar(irmao, x.pai.cor)
                    self._pintar(x.pai, PRETO)
                    self._pintar(irmao.esq, PRETO)
                    self._rotacao_direita(x.pai)
                    x = self.raiz
        self._pintar(x, PRETO)

    # ------------------------------------------------------------------
    # Desenho e validação
    # ------------------------------------------------------------------
    def _rotulo(self, no):
        return f"#{no.chave} [{'V' if no.cor == VERMELHO else 'P'}]"

    def validar(self):
        super().validar()
        nil = self._nil
        assert nil.cor == PRETO, "a sentinela não é preta"
        assert nil.esq is nil and nil.dir is nil and nil.pai is nil, "a sentinela foi alterada"
        if self.raiz is nil:
            return
        assert self.raiz.cor == PRETO, "a raiz não é preta"
        assert self.raiz.pai is nil, "a raiz tem pai"
        self._validar_no(self.raiz)

    def _validar_no(self, no):
        """Devolve a altura preta da subárvore e confere cores e ponteiros para o pai."""
        if no is self._nil:
            return 1  # a folha vazia é preta
        assert no.cor in (VERMELHO, PRETO), f"cor inválida em #{no.chave}"
        for filho in (no.esq, no.dir):
            assert filho is self._nil or filho.pai is no, f"#{filho.chave} aponta para o pai errado"
            assert not (no.cor == VERMELHO and filho.cor == VERMELHO), f"#{no.chave} vermelho com filho vermelho"
        pretos_esq = self._validar_no(no.esq)
        pretos_dir = self._validar_no(no.dir)
        assert pretos_esq == pretos_dir, f"altura preta diferente nos dois lados de #{no.chave}"
        return pretos_esq + (1 if no.cor == PRETO else 0)
