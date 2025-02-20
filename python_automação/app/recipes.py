import psycopg2
from config.settings import DB_CONFIG

def get_recipe_from_db(recipe_name):
    """Recupera a sequência de produtos da receita do banco de dados."""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        # Pega os produtos da receita ordenados pelos passos
        cursor.execute("SELECT step, produto_nome FROM receita_produtos WHERE receita_nome = %s ORDER BY step;", (recipe_name,))
        result = cursor.fetchall()
        cursor.close()
        return result
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Erro ao recuperar a receita do banco de dados: {error}")
        return None
    finally:
        if conn is not None:
            conn.close()
