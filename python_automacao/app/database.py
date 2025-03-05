import pyodbc
import sys
import os
import time
from datetime import datetime

# Adiciona o diretório "python_automacao" ao sys.path.
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_dir)
print("sys.path:", sys.path)

# Importa as classes atualizadas
from Variaveis_Teste.Receita import Receita, Receita2, Produto, Lote

server = 'FULVIO\\FULVIO'        # Ex: 'localhost\\SQLEXPRESS'
database = 'UBY_ORIGIANAL'
username = 'sa'
password = '123456'

# Criação da string de conexão
DB_CONFIG = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password}'
)

def Conexao_SQLSERVER(DB_CONFIG):
    try:
        cnxn = pyodbc.connect(DB_CONFIG)
        cursor = cnxn.cursor()
        print("Conexão estabelecida com sucesso!")
        # Exibe versão do SQL Server
        cursor.execute("SELECT @@version;")
        row = cursor.fetchone()
        while row:
            print(row[0])
            row = cursor.fetchone()
        return cursor
    except Exception as e:
        print("Erro ao conectar ao SQL Server:", e)
        return None

def consulta_produto_lote(cursor, numero_produto):
    """
    Consulta um produto global e seu lote, juntando as tabelas [Receita], [ReceitaProduto], 
    [ProdutoGlobal] e [Lote]. Retorna os dados que correspondem a um determinado número de produto
    e número de lote.
    """
    query = """
    SELECT 
        r.receita_id,
        r.nome_receita,
        rp.receita_id AS rp_receita_id,
        rp.produto_id,
        pg.numero_produto,
        rp.quantidade_total,
        pg.nome AS produto_nome,
        l.lote_id,
        l.observacao_lote,
        l.quantidade_lote,
        l.peso_lote
    FROM [Receita] r
    JOIN [ReceitaProduto] rp ON r.receita_id = rp.receita_id
    JOIN [ProdutoGlobal] pg ON rp.produto_id = pg.produto_id
    JOIN [Lote] l ON pg.produto_id = l.produto_id
    WHERE pg.numero_produto = ? 
    """
    cursor.execute(query, (numero_produto,))
    rows = cursor.fetchall()
    return rows

def get_receita_from_db_novo(cursor, receita_id):
    """
    Consulta a receita com todos os produtos e seus lotes a partir das tabelas:
    [Receita], [ReceitaProduto], [ProdutoGlobal] e [Lote].
    Instancia os objetos conforme as classes Receita2, Produto e Lote.
    """
    query = """
    SELECT 
        r.receita_id,
        r.nome_receita,
        r.produto_numero,
        pg.produto_id,
        pg.numero_produto,
        rp.quantidade_total,
        pg.nome AS produto_nome,
        l.lote_id,
        l.observacao_lote,
        l.quantidade_lote,
        l.peso_lote
    FROM [Receita] r
    JOIN [ReceitaProduto] rp ON r.receita_id = rp.receita_id
    JOIN [ProdutoGlobal] pg ON rp.produto_id = pg.produto_id
    JOIN [Lote] l ON pg.produto_id = l.produto_id
    WHERE r.receita_id = ?
    ORDER BY pg.numero_produto;
    """
    cursor.execute(query, (receita_id,))
    rows = cursor.fetchall()
    
    if not rows:
        print("Nenhum dado encontrado para a receita.")
        return None

    # Agrupa os produtos pela coluna 'numero_produto'
    produtos_dict = {}
    for row in rows:
        num_produto = row.numero_produto
        if num_produto not in produtos_dict:
            produtos_dict[num_produto] = {
                "produto_id": row.produto_id,
                "quantidade_total": row.quantidade_total,
                "produto_nome": row.produto_nome,
                "lotes": []
            }
        # Cria o objeto Lote com os campos da nova modelagem
        lote_obj = Lote(
            lote_id=row.lote_id,
            quantidade_lote = row.quantidade_lote,
            peso_lote = row.peso_lote,
            observacao_lote = row.observacao_lote
        )
        produtos_dict[num_produto]["lotes"].append(lote_obj)
    
    produtos_list = []
    for num_produto, dados in produtos_dict.items():
        try:
            produto_obj = Produto(
                numero_produto = num_produto,
                quantidade_total = dados["quantidade_total"],
                nome = dados["produto_nome"],
                lotes = dados["lotes"]
            )
            produtos_list.append(produto_obj)
        except ValueError as ve:
            print(f"Erro ao criar produto {num_produto}: {ve}")
    
    receita_obj = Receita2(
        receita_id = receita_id,
        produto_numero = rows[0].produto_numero,
        nome_receita = rows[0].nome_receita,
        produtos = produtos_list
    )
    return receita_obj

def Qnt_total_lotes_receitas_nova(cursor, receita_id):
    query = """
    SELECT COUNT(l.lote_id) AS total_lotes
    FROM [Receita] r
    JOIN [ReceitaProduto] rp ON r.receita_id = rp.receita_id
    JOIN [ProdutoGlobal] pg ON rp.produto_id = pg.produto_id
    JOIN [Lote] l ON pg.produto_id = l.produto_id
    WHERE r.receita_id = ?
    """
    cursor.execute(query, (receita_id,))
    row = cursor.fetchone()
    return row.total_lotes

def quantidade_produtos_receita_nova(cursor, receita_id):
    query = """
    SELECT COUNT(rp.produto_id) AS total_produtos
    FROM [Receita] r
    JOIN [ReceitaProduto] rp ON r.receita_id = rp.receita_id
    WHERE r.receita_id = ?
    """
    cursor.execute(query, (receita_id,))
    row = cursor.fetchone()
    return row.total_produtos

def envio_pesos_lote_salvo_novo(cursor, receita_id, vetor_peso_lote):
    """
    Lê os lotes associados à receita (via [Receita], [ReceitaProduto], [ProdutoGlobal] e [Lote])
    e insere registros na tabela 'lote_salvo' com o peso real medido.
    """
    query = """
    SELECT 
        pg.produto_id,
        l.observacao_lote,
        l.quantidade_lote
    FROM [Receita] r
    JOIN [ReceitaProduto] rp ON r.receita_id = rp.receita_id
    JOIN [ProdutoGlobal] pg ON rp.produto_id = pg.produto_id
    JOIN [Lote] l ON pg.produto_id = l.produto_id
    WHERE r.receita_id = ?
    ORDER BY pg.numero_produto;
    """
    cursor.execute(query, (receita_id,))
    rows = cursor.fetchall()
    if not rows:
        print(f"Nenhum lote encontrado para a receita {receita_id}.")
        return
    total_lotes = len(rows)
    print("Total de lotes:", total_lotes)
    if len(vetor_peso_lote) != total_lotes:
        print(f"Erro: Esperados {total_lotes} pesos, mas foram fornecidos {len(vetor_peso_lote)}.")
        return
    insert_query = """
    INSERT INTO lote_salvo (
        produto_id,
        observacao_lote,
        quantidade_lote,
        peso_real,
        data_insercao
    ) VALUES (?, ?, ?, ?, ?);
    """
    data_atual = datetime.now()
    for i, row in enumerate(rows):
        produto_id = row.produto_id
        observacao_lote = row.observacao_lote
        quantidade_lote = row.quantidade_lote
        peso_real = vetor_peso_lote[i]
        print(produto_id,  observacao_lote, quantidade_lote, peso_real, data_atual)
        cursor.execute(insert_query, (
            produto_id,
            observacao_lote,
            quantidade_lote,
            peso_real,
            data_atual
        ))
    cursor.connection.commit()
    print("Pesos inseridos com sucesso em 'lote_salvo'!")

# MAIN - Teste de todas as funções do sistema
if __name__ == "__main__":
    cursor = Conexao_SQLSERVER(DB_CONFIG)
    if cursor:
        # Define o ID da receita de teste conforme inserido no banco
        receita_id_teste = 200000060359
        
        print("\n=== Consulta Produto Lote ===")
        # Exemplo: consulta um produto com número 1 e lote 1
        #resultado_pl = consulta_produto_lote(cursor, 1)
        #for row in resultado_pl:
            #print(row)
        
        print("\n=== Consulta Receita ===")
        receita_obj = get_receita_from_db_novo(cursor, receita_id_teste)
        #print(receita_obj)
        
        
        
        
        print("receita",receita_obj.nome_receita)
        print("produtos",receita_obj.produtos)
        #print("produtos[0]",receita_obj.produtos[0])
        print("produtos[0].lotes[0]",receita_obj.produtos[0].lotes[0])
        print("Quantidade produto 1", receita_obj.produtos[0].quantidade_total)
        print("Quantidade produto 2", receita_obj.produtos[1].quantidade_total)
        print("QUantidade do lote 1 do produto 1",receita_obj.produtos[0].lotes[0].quantidade_lote)
        print("QUantidade do lote 2 do produto 1",receita_obj.produtos[1].lotes[0].quantidade_lote)
        
        print("Quantidade total de lote",len(receita_obj.produtos[0].lotes))
        print("Observacao lote 1",receita_obj.produtos[0].lotes[0].observacao_lote)
        #print("produtos[1]",receita_obj.produtos[1])
        #print("produtos[1].lotes[0]",receita_obj.produtos[1].lotes[0])
        print("Quantidade de lote no produto",len(receita_obj.produtos[0].lotes))
        
        
        
        
        total_lotes = Qnt_total_lotes_receitas_nova(cursor, receita_id_teste)
        #print(f"\nReceita {receita_id_teste}: Total de lotes = {total_lotes}")
        
        #total_produtos = quantidade_produtos_receita_nova(cursor, receita_id_teste)
        #print(f"Receita {receita_id_teste}: Total de produtos = {total_produtos}")
        
        #print("\n=== Envio de Pesos para 'lote_salvo' ===")
        # Exemplo: vetor de pesos para cada lote (todos com 1.2 para teste)
        #vetor_pesos = [1.2] * total_lotes
        #envio_pesos_lote_salvo_novo(cursor, receita_id_teste, vetor_pesos)
        
        cursor.close()

