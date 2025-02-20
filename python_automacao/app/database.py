import pyodbc
from Variaveis_Teste.Receita import Receita, Produto, Lote

server = 'FULVIO\\FULVIO'        # Ex: 'localhost\SQLEXPRESS'
database = 'TESTE'           # Ex: 'meuBanco'
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
        
        # Exemplo de consulta
        cursor.execute("SELECT @@version;")
        row = cursor.fetchone()
        while row:
            print(row[0])
            row = cursor.fetchone()

    except Exception as e:
        print("Erro ao conectar ao SQL Server:", e)



def consulta_produto_lote(cursor, numero_produto, numero_lote):
    query = """
    SELECT 
        r.id AS receita_id,
        r.observacao AS receita_observacao,
        p.id AS produto_id,
        p.numero_produto,
        p.qtd_produto,
        p.observacao AS produto_observacao,
        l.id AS lote_id,
        l.numero_lote,
        l.identificacao_lote,
        l.qtd_produto_cada_lote
    FROM receita r
    JOIN produto p ON r.id = p.receita_id
    JOIN lote l ON p.id = l.produto_id
    WHERE p.numero_produto = ? AND l.numero_lote = ?;
    """
    cursor.execute(query, (numero_produto, numero_lote))
    rows = cursor.fetchall()
    return rows



def get_receita_from_db(cursor, receita_id):
    """
    Consulta a receita com todos os produtos e lotes e instancia os objetos 
    de acordo com as classes Receita, Produto e Lote.
    """
    query = """
    SELECT 
        r.id as receita_id,
        r.observacao as receita_observacao,
        p.numero_produto,
        p.qtd_produto,
        p.observacao as produto_observacao,
        l.numero_lote,
        l.identificacao_lote,
        l.qtd_produto_cada_lote
    FROM receita r
    JOIN produto p ON r.id = p.receita_id
    JOIN lote l ON p.id = l.produto_id
    WHERE r.id = ?
    ORDER BY p.numero_produto, l.numero_lote;
    """
    cursor.execute(query, (receita_id,))
    rows = cursor.fetchall()
    
    if not rows:
        print("Nenhum dado encontrado para a receita.")
        return None

    # Cria um dicionário para agrupar os dados por produto.
    produtos_dict = {}
    for row in rows:
        num_produto = row.numero_produto
        if num_produto not in produtos_dict:
            produtos_dict[num_produto] = {
                "qtd_produto": row.qtd_produto,
                "observacao": row.produto_observacao,
                "lotes": []
            }
        # Cria o objeto Lote para cada linha.
        lote_obj = Lote(
            numero_lote=row.numero_lote,
            identificacao_lote=row.identificacao_lote,
            qtd_produto_cada_lote=row.qtd_produto_cada_lote
        )
        produtos_dict[num_produto]["lotes"].append(lote_obj)
    
    # Cria a lista de objetos Produto
    produtos_list = []
    for num_produto, dados in produtos_dict.items():
        try:
            produto_obj = Produto(
                numero_produto=num_produto,
                qtd_produto=dados["qtd_produto"],
                lotes=dados["lotes"],
                observacao=dados["observacao"]
            )
            produtos_list.append(produto_obj)
        except ValueError as ve:
            print(f"Erro ao criar produto {num_produto}: {ve}")
            # Caso a soma dos lotes não seja igual à qtd_produto, o ValueError é lançado.
    nome_receita = rows[0].receita_observacao
    # Cria a Receita com a lista de produtos
    receita_obj = Receita(produtos=produtos_list,nome_receita=nome_receita)
    return receita_obj


'''try:
    cnxn = pyodbc.connect(DB_CONFIG)
    cursor = cnxn.cursor()
    receita_id = 1  # ou outro id desejado
    resultado = consulta_produto_lote(cursor, receita_id,3)

    
    for row in resultado:
        print(row)
    
except Exception as e:
    print("Erro na conexão ou consulta:", e)'''



