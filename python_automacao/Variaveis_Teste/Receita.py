class Lote:
    def __init__(self, lote_id, quantidade_lote, peso_lote, observacao_lote):
        """
        :param lote_id: Identificador único do lote (gerado pelo banco).
        :param quantidade_lote: Quantidade do lote.
        :param peso_lote: Peso do lote.
        :param observacao_lote: Observações sobre o lote.
        """
        self.lote_id = lote_id
        self.quantidade_lote = quantidade_lote
        self.peso_lote = peso_lote
        self.observacao_lote = observacao_lote

    def __str__(self):
        return (f"LoteID: {self.lote_id}, Quantidade: {self.quantidade_lote}, "
                f"Peso: {self.peso_lote}, Obs: {self.observacao_lote}")

    def __repr__(self):
        return self.__str__()


class Produto:
    def __init__(self, numero_produto, quantidade_total, nome, lotes):
        """
        :param numero_produto: Número do produto (pode ser repetido em diferentes receitas).
        :param quantidade_total: Quantidade total requerida para o produto na receita (do campo quantidade_total de ReceitaProduto).
        :param nome: Nome do produto (informação da tabela ProdutoGlobal).
        :param lotes: Lista de objetos Lote (os lotes associados a esse produto na receita).
        """
        self.numero_produto = numero_produto
        self.quantidade_total = quantidade_total
        self.nome = nome
        self.lotes = lotes

        total_lotes = sum(lote.quantidade_lote for lote in lotes)
        if total_lotes != quantidade_total:
            raise ValueError(
                f"A soma das quantidades dos lotes ({total_lotes}) não é igual à quantidade total do produto ({quantidade_total})."
            )

    def __str__(self):
        lotes_str = "\n  ".join(str(lote) for lote in self.lotes)
        return (f"Produto {self.numero_produto} - {self.nome}:\n"
                f"Quantidade Total: {self.quantidade_total}\n"
                f"Lotes:\n  {lotes_str}")

    def __repr__(self):
        return self.__str__()


class Receita:
    def __init__(self, produto_numero, nome_receita, produtos):
        """
        :param produto_numero: Número de produtos associados à receita.
        :param nome_receita: Nome ou observação da receita.
        :param produtos: Lista de objetos Produto que compõem a receita.
        """
        self.produto_numero = produto_numero
        self.nome_receita = nome_receita
        self.produtos = produtos

    def __str__(self):
        produtos_str = "\n\n".join(str(produto) for produto in self.produtos)
        return (f"Receita {self.nome_receita} (Produtos: {self.produto_numero}):\n"
                f"{produtos_str}")

    def __repr__(self):
        return self.__str__()


class Receita2:
    def __init__(self, receita_id, produto_numero, nome_receita, produtos):
        """
        :param receita_id: ID da receita (do campo receita_id da tabela Receita).
        :param produto_numero: Número de produtos associados à receita.
        :param nome_receita: Nome da receita.
        :param produtos: Lista de objetos Produto que compõem a receita.
        """
        self.receita_id = receita_id
        self.produto_numero = produto_numero
        self.nome_receita = nome_receita
        self.produtos = produtos

    def __str__(self):
        produtos_str = "\n\n".join(str(produto) for produto in self.produtos)
        return (f"Receita {self.nome_receita} (ID: {self.receita_id}, Produtos: {self.produto_numero}):\n"
                f"{produtos_str}")

    def __repr__(self):
        return self.__str__()
