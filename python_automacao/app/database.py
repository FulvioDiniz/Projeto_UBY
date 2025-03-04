import pyodbc
from Variaveis_Teste.Receita import Receita, Produto, Lote
import time
from datetime import datetime
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


def Qnt_total_lotes_receitas(cursor, receita_id):
    query = """
    SELECT 
        COUNT(l.id) AS total_lotes
    FROM receita r
    JOIN produto p ON r.id = p.receita_id
    JOIN lote l ON p.id = l.produto_id
    WHERE r.id = ?;
    """
    cursor.execute(query, (receita_id,))
    row = cursor.fetchone()
    return row.total_lotes


def verifica_receita_nova_no_db(cursor, receita_id):
    query = "SELECT COUNT(*) FROM receita WHERE id = ?;"
    cursor.execute(query, (receita_id,))
    row = cursor.fetchone()
    return row[0] > 0


def envio_pesos_lote_erp(cursor, receita_id, vetor_peso_lote):
    query = """
            SELECT 
                p.observacao AS produto_observacao
                FROM produto p
                JOIN receita r ON r.id = p.receita_id
                WHERE r.id = ?
                ORDER BY p.numero_produto;

    """
    cursor.execute(query, (receita_id))
    cursor.commit()
    lista_produtos = cursor.fetchall()
    print(lista_produtos)
    query_envia_peso = "INSERT INTO  lote_enviado(receita_id,produto,qtd_produto_cada_lote,data) VALUES (?,?,?,?);"
    data = time.strftime('%D-%M-%Y %H:%M:%S')
    for i in range(len(vetor_peso_lote)):
        cursor.execute(query_envia_peso, (receita_id,lista_produtos[i], vetor_peso_lote[i],data))
        cursor.commit()
    cursor.close()
    
    
    
    
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
    
import pyodbc
from datetime import datetime

def envio_pesos_lote_salvo(cursor, receita_id, vetor_peso_lote):
    """
    Lê os lotes associados a uma receita (join de receita→produto→lote)
    e insere registros em 'lote_salvo' com o peso real medido (peso_real).

    - 'receita_id': ID da receita na tabela 'receita'
    - 'vetor_peso_lote': lista de pesos reais, correspondentes aos lotes em ordem
    """
    # 1) Busca informações de cada lote vinculado à receita (produto + lote)
    query = """
        SELECT
            p.id            AS produto_id,
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
        print(f"Nenhum lote encontrado para a receita {receita_id}.")
        return

    # 2) Verifica se o 'vetor_peso_lote' combina com a quantidade de lotes
    total_lotes = len(rows)
    print("total lote",total_lotes)
    vetor_p = len(vetor_peso_lote)
    print("total vetor peso", vetor_p)
    if len(vetor_peso_lote) != total_lotes:
        print(f"Erro: Esperados {total_lotes} pesos, mas foram fornecidos {len(vetor_peso_lote)}.")
        return

    # 3) Prepara o INSERT na nova tabela 'lote_salvo'
    #    Agora incluindo 'data_insercao' na lista de colunas
    insert_query = """
        INSERT INTO lote_salvo (
            produto_id,
            numero_lote,
            identificacao_lote,
            qtd_produto_cada_lote,
            peso_real,
            data_insercao
        ) VALUES (?, ?, ?, ?, ?, ?);
    """

    # 4) Insere cada lote na tabela 'lote_salvo', associando o peso real do vetor
    #    e armazenando a data/hora de inserção
    data_atual = datetime.now()
    for i, row in enumerate(rows):
        produto_id          = row.produto_id
        numero_lote         = row.numero_lote
        identificacao_lote  = row.identificacao_lote
        qtd_cada_lote       = row.qtd_produto_cada_lote
        peso_real           = vetor_peso_lote[i]  # valor real medido do lote
        print(produto_id,numero_lote,identificacao_lote,qtd_cada_lote,peso_real,data_atual)

        cursor.execute(insert_query, (
            produto_id,
            numero_lote,
            identificacao_lote,
            qtd_cada_lote,
            peso_real,
            data_atual  # data/hora de inserção
        ))

    # 5) Confirma as inserções
    cursor.connection.commit()
    print("Pesos inseridos com sucesso em 'lote_salvo'!")



'''def valida_receita(cursor, receita_id):
    """
    Verifica se a receita existe no banco de dados.
    """
    query = "SELECT COUNT(*) FROM receita WHERE id = ?;"
    cursor.execute(query, (receita_id,))
    if cursor.fetchone()[0] == 0:
        print(f"Receita {receita_id} não encontrada.")
        return False
    return True'''