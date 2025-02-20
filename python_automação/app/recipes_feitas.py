import psycopg2
from config.settings import DB_CONFIG
from datetime import datetime

def save_recipe_step_to_db(recipe_name, step, product_name, weight, confirmed):
    """Salva o passo, produto, peso, data e confirmação da receita no banco de dados."""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        # Insere o nome da receita, passo, produto, peso, data e status de confirmação
        cursor.execute(
            "INSERT INTO receitas_feitas (receita_nome, step, produto_nome, peso, data_hora, confirmado) VALUES (%s, %s, %s, %s, %s, %s);",
            (recipe_name, step, product_name, weight, datetime.now(), confirmed)
        )
        conn.commit()
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Erro ao salvar a execução da receita no banco de dados: {error}")
    finally:
        if conn is not None:
            conn.close()

def confirm_recipe_step_in_db(recipe_name, step, product_name):
    """Confirma a execução de um passo da receita e salva a data/hora no banco de dados."""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        # Atualiza o status de confirmação e salva a data/hora da confirmação
        cursor.execute(
            "UPDATE receitas_feitas SET confirmado = TRUE, data_hora = %s WHERE receita_nome = %s AND step = %s AND produto_nome = %s;",
            (datetime.now(), recipe_name, step, product_name)
        )
        conn.commit()
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Erro ao confirmar o passo no banco de dados: {error}")
    finally:
        if conn is not None:
            conn.close()
