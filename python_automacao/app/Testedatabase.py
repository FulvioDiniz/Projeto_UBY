import pyodbc
from datetime import datetime

# Configuração do banco
server = 'FULVIO\\FULVIO'
database = 'TESTE'
username = 'sa'
password = '123456'

DB_CONFIG = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password}'
)


    
def quantidade_produtos_receita(cursor, receita_id):
    query = """
    SELECT 
        COUNT(p.id) AS total_produtos
    FROM receita r
    JOIN produto p ON r.id = p.receita_id
    WHERE r.id = ?;
    """
    cursor.execute(query, (receita_id,))
    row = cursor.fetchone()
    return row.total_produtos


def envio_pesos_lote_erp(cursor, receita_id, vetor_peso_lote):
    query = """
        SELECT p.observacao AS produto_observacao
        FROM produto p
        JOIN receita r ON r.id = p.receita_id
        WHERE r.id = ?
        ORDER BY p.numero_produto;
    """
    
    cursor.execute(query, (receita_id,))
    lista_produtos = cursor.fetchall()
    
    if not lista_produtos:
        print(f"Nenhum produto encontrado para a receita: {receita_id}")
        return

    print("Produtos encontrados:", lista_produtos)

    num_produtos = len(lista_produtos)
    num_lotes_por_produto = 4
    total_pesos_esperados = num_produtos * num_lotes_por_produto

    if len(vetor_peso_lote) != total_pesos_esperados:
        print(f"Erro: Esperados {total_pesos_esperados} pesos, mas foram fornecidos {len(vetor_peso_lote)}.")
        return
    
    query_envia_peso = """
        INSERT INTO lote_enviado (receita_id, produto, qtd_produto_cada_lote, data) 
        VALUES (?, ?, ?, ?);
    """

    data = datetime.now()  # Enviar como objeto datetime, não string

    index_peso = 0
    for produto in lista_produtos:  
        for lote in range(num_lotes_por_produto):  
            cursor.execute(query_envia_peso, (receita_id, produto[0], vetor_peso_lote[index_peso], data))
            index_peso += 1  

    cnxn.commit()
    print("Pesos enviados com sucesso!")

try:
    cnxn = pyodbc.connect(DB_CONFIG)
    cursor = cnxn.cursor()
    
    receita_id_teste = 20020111
    num_produtos_teste = quantidade_produtos_receita(cursor, receita_id_teste)
    num_lotes_por_produto = 4

    vetor_peso_lote_teste = [3000.0, 2004.0, 1500.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    envio_pesos_lote_erp(cursor, receita_id_teste, vetor_peso_lote_teste)

    cursor.execute("SELECT * FROM lote_enviado WHERE receita_id = ?", (receita_id_teste,))
    rows = cursor.fetchall()

    print("Dados inseridos em lote_enviado:")
    for row in rows:
        print(row)

except Exception as e:
    print("Erro ao conectar ou inserir no SQL Server:", e)

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'cnxn' in locals():
        cnxn.close()
    print("Conexão fechada.")
