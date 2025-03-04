import pyodbc
from datetime import datetime

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

        # Exemplo: suponha que a receita com ID=20020111 tem 8 lotes no total.
        receita_id_exemplo = 20020111

        # Exemplo de vetor de 8 pesos medidos pelo operador ou CLP (todos fictícios).
        vetor_pesos_medidos = [3560.0, 0.0, 0.0, 0.0, 250.0, 101.0, 205.0, 0.0, 205.0, 302.0, 0.0, 0.0, 101.0, 55.0, 56.0, 55.0, 60.0, 105.0, 0.0, 0.0, 105.0, 0.0, 0.0, 0.0, 260.0, 280.0, 0.0, 0.0, 30.0, 0.0, 0.0, 0.0]


        # Chama a função para inserir em 'lote_salvo'
        envio_pesos_lote_salvo(cursor, receita_id_exemplo, vetor_pesos_medidos)

    except Exception as e:
        print("Erro ao conectar ou inserir no SQL Server:", e)

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass
