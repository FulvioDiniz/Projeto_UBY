import pyodbc
from datetime import datetime
import sys
import os


# Adiciona o diretório "python_automacao" ao sys.path.
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_dir)
print("sys.path:", sys.path)

from Variaveis_Teste.Receita import Receita2, Produto, Lote

def get_receita_from_db_novo(cursor, receita_id):
    """
    Consulta a receita com todos os produtos e lotes a partir das tabelas
    'receita2', 'produto2' e 'lote2', instanciando os objetos de acordo com as classes
    Receita2, Produto e Lote.
    
    - 'receita_id': ID da receita na tabela 'receita2'
    """
    query = """
    SELECT 
        r.id AS receita_id,
        r.observacao AS receita_observacao,
        r.produto_id AS pord,
        p.id AS produto_id,
        p.numero_produto,
        p.qtd_produto,
        p.observacao AS produto_observacao,
        l.id AS lote_id,
        l.numero_lote,
        l.identificacao_lote,
        l.qtd_produto_cada_lote
    FROM receita2 r
    JOIN produto2 p ON r.id = p.receita_id
    JOIN lote2 l ON p.id = l.produto_id
    WHERE r.id = ?
    ORDER BY p.numero_produto, l.numero_lote;
    """
    cursor.execute(query, (receita_id,))
    rows = cursor.fetchall()
    
    if not rows:
        print("Nenhum dado encontrado para a receita.")
        return None

    # Obtém os parâmetros da receita a partir da primeira linha
    receita_id_val = rows[0].receita_id
    nome_receita = rows[0].receita_observacao
    pord_val = rows[0].pord

    # Agrupa os dados por produto, utilizando o 'numero_produto' como chave.
    produtos_dict = {}
    for row in rows:
        num_produto = row.numero_produto
        if num_produto not in produtos_dict:
            produtos_dict[num_produto] = {
                "produto_id": row.produto_id,  # Campo adicional, se necessário
                "qtd_produto": row.qtd_produto,
                "observacao": row.produto_observacao,
                "lotes": []
            }
        # Instancia um objeto Lote para cada registro
        lote_obj = Lote(
            numero_lote=row.numero_lote,
            identificacao_lote=row.identificacao_lote,
            qtd_produto_cada_lote=row.qtd_produto_cada_lote
        )
        produtos_dict[num_produto]["lotes"].append(lote_obj)
    
    # Converte os dados agrupados em uma lista de objetos Produto
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
            # Se houver inconsistência (por exemplo, a soma dos lotes não corresponder à qtd_produto),
            # um ValueError poderá ser lançado.
    
    # Instancia o objeto Receita2 com os novos parâmetros
    receita_obj = Receita2(
        receita_id=receita_id_val,
        nome_receita=nome_receita,
        pord=pord_val,
        produtos=produtos_list
    )
    return receita_obj



if __name__ == "__main__":
    connection_string = (
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=FULVIO\\FULVIO;'
        'DATABASE=TESTE;'
        'UID=sa;'
        'PWD=123456'
    )

    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        print("Conexão estabelecida com sucesso!")

        receita_id = 2000000060359
        vetor_volta_db = get_receita_from_db_novo(cursor, receita_id)
        print(vetor_volta_db)

    except Exception as e:
        print("Erro ao conectar ou inserir no SQL Server:", e)

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass
