class Lote:
    def __init__(self, numero_lote, identificacao_lote, qtd_produto_cada_lote):
        self.numero_lote = numero_lote
        self.identificacao_lote = identificacao_lote
        self.qtd_produto_cada_lote = qtd_produto_cada_lote

    def __str__(self):
        return (f"NumeroLote: {self.numero_lote}, "
                f"Identificacao: {self.identificacao_lote}, "
                f"Quantidade: {self.qtd_produto_cada_lote}")

    def __repr__(self):
        return self.__str__()


class Produto:
    def __init__(self, numero_produto, qtd_produto, lotes, observacao=""):
        """
        :param numero_produto: identificador do produto.
        :param qtd_produto: quantidade máxima/total do produto.
        :param lotes: lista de objetos Lote que compõem o produto.
        :param observacao: observações adicionais.
        """
        self.numero_produto = numero_produto
        self.qtd_produto = qtd_produto
        self.lotes = lotes
        self.observacao = observacao

        # Validação: a soma das quantidades dos lotes deve ser exatamente igual à quantidade máxima do produto.
        total_lotes = sum(lote.qtd_produto_cada_lote for lote in lotes)
        if total_lotes != qtd_produto:
            raise ValueError(
                f"A soma das quantidades dos lotes ({total_lotes}) deve ser igual à quantidade máxima do produto ({qtd_produto})."
            )

    def __str__(self):
        lotes_str = "\n  ".join(str(lote) for lote in self.lotes)
        return (f"Produto {self.numero_produto}:\n"
                f"Quantidade: {self.qtd_produto}\n"
                f"Observacao: {self.observacao}\n"
                f"Lotes:\n  {lotes_str}")

    def __repr__(self):
        return self.__str__()


class Receita:
    def __init__(self, produtos,nome_receita):
        """
        :param produtos: lista de objetos Produto que compõem a receita.
        """
        self.produtos = produtos
        self.nome_receita = nome_receita

    def __str__(self):
        produtos_str = "\n\n".join(str(produto) for produto in self.produtos)
        return (f"Receita {self.nome_receita}:\n"
                f"Produtos:\n\n{produtos_str}")
    