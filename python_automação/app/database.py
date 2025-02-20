import pyodbc

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

def consulta_receita(cursor, receita_id):
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
    WHERE r.id = ?
    ORDER BY p.numero_produto, l.numero_lote;
    """
    cursor.execute(query, (receita_id,))
    # Recupera todas as linhas do resultado
    rows = cursor.fetchall()
    return rows

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






'''try:
    cnxn = pyodbc.connect(DB_CONFIG)
    cursor = cnxn.cursor()
    receita_id = 1  # ou outro id desejado
    resultado = consulta_produto_lote(cursor, receita_id,3)

    
    for row in resultado:
        print(row)
    
except Exception as e:
    print("Erro na conexão ou consulta:", e)'''