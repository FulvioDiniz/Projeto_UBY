import pyodbc
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'MUDE_PARA_UMA_CHAVE_SECRETA_QUALQUER' 

CONN_STR = (
    r'DRIVER={ODBC Driver 17 for SQL Server};'
    r'SERVER=FULVIO\FULVIO;'
    r'DATABASE=Banco reformulado;'
    r'UID=sa;'
    r'PWD=123456;'
)

# <<<<<<<<<<<<<<<< ALTERAÇÃO 1 AQUI >>>>>>>>>>>>>>>>>
def get_db_conn():
    """Cria e retorna uma nova conexão com o banco, com autocommit DESLIGADO."""
    try:
        # Forçamos o modo de transação manual, que é o padrão e mais seguro.
        conn = pyodbc.connect(CONN_STR, autocommit=False)
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

# --- Rotas da Aplicação ---
# (As outras rotas como index, criar_receita, etc., continuam iguais e corretas)
@app.route('/')
def index():
    conn = get_db_conn()
    receitas = []
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT receita_id, nome_receita, produto_numero FROM Receita ORDER BY nome_receita")
        receitas = cursor.fetchall()
        conn.close()
    return render_template('index.html', receitas=receitas)

@app.route('/receita/nova', methods=['GET', 'POST'])
def criar_receita():
    if request.method == 'POST':
        receita_id = request.form['receita_id']
        nome_receita = request.form['nome_receita']
        produto_numero = request.form['produto_numero']
        conn = get_db_conn()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO Receita (receita_id, nome_receita, produto_numero) VALUES (?, ?, ?)", 
                               receita_id, nome_receita, produto_numero)
                conn.commit() # Commit aqui continua necessário e correto
                flash('Receita criada com sucesso!', 'success')
                return redirect(url_for('detalhe_receita', receita_id=receita_id))
            except Exception as e:
                conn.rollback()
                flash(f'Erro ao criar receita: {e}', 'danger')
            finally:
                conn.close()
    return render_template('criar_receita.html')

@app.route('/receita/<int:receita_id>')
def detalhe_receita(receita_id):
    conn = get_db_conn()
    receita, produtos_na_receita, produtos_globais, lotes_por_produto = None, [], [], {}
    if conn:
        cursor = conn.cursor()
        receita = cursor.execute("SELECT * FROM Receita WHERE receita_id = ?", receita_id).fetchone()
        sql_produtos_receita = """
            SELECT rp.receita_produto_id, pg.produto_id, pg.numero_produto, pg.nome, rp.quantidade_total 
            FROM ReceitaProduto rp JOIN ProdutoGlobal pg ON rp.produto_id = pg.produto_id
            WHERE rp.receita_id = ? ORDER BY pg.nome
        """
        produtos_na_receita = cursor.execute(sql_produtos_receita, receita_id).fetchall()
        for produto in produtos_na_receita:
            sql_lotes = """
                SELECT l.observacao_lote, l.peso_lote, rpl.quantidade_utilizada
                FROM Lote l JOIN ReceitaProdutoLote rpl ON l.lote_id = rpl.lote_id
                WHERE rpl.receita_produto_id = ? ORDER BY l.lote_id
            """
            lotes = cursor.execute(sql_lotes, produto.receita_produto_id).fetchall()
            lotes_por_produto[produto.receita_produto_id] = lotes
        cursor.execute("SELECT produto_id, nome FROM ProdutoGlobal ORDER BY nome")
        produtos_globais = cursor.fetchall()
        conn.close()
    if not receita:
        flash('Receita não encontrada.', 'danger')
        return redirect(url_for('index'))
    return render_template('detalhe_receita.html', receita=receita, produtos_na_receita=produtos_na_receita, produtos_globais=produtos_globais, lotes_por_produto=lotes_por_produto)

@app.route('/receita/adicionar_produto', methods=['POST'])
def adicionar_produto_receita():
    receita_id = request.form['receita_id']
    produto_id = request.form['produto_id']
    quantidade_total = request.form['quantidade_total']
    conn = get_db_conn()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO ReceitaProduto (receita_id, produto_id, quantidade_total) VALUES (?, ?, ?)",
                           receita_id, produto_id, quantidade_total)
            conn.commit()
            flash('Produto adicionado à receita com sucesso!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Erro ao adicionar produto: {e}', 'danger')
        finally:
            conn.close()
    return redirect(url_for('detalhe_receita', receita_id=receita_id))

# <<<<<<<<<<<<<<<< ALTERAÇÃO 2 AQUI >>>>>>>>>>>>>>>>>
@app.route('/receita/adicionar_lote', methods=['POST'])
def adicionar_lote():
    receita_id = request.form['receita_id']
    produto_id = request.form['produto_id']
    receita_produto_id = request.form['receita_produto_id']
    peso_lote = request.form['peso_lote']
    observacao = request.form['observacao_lote']
    quantidade_lote = peso_lote
    quantidade_utilizada = peso_lote
    conn = get_db_conn()
    if conn:
        cursor = conn.cursor()
        try:
            # O "BEGIN TRANSACTION" foi removido. O pyodbc já inicia uma transação
            # porque autocommit=False.
            sql_insert_com_output = """
                INSERT INTO Lote (produto_id, quantidade_lote, peso_lote, observacao_lote)
                OUTPUT inserted.lote_id
                VALUES (?, ?, ?, ?);
            """
            lote_id = cursor.execute(sql_insert_com_output, produto_id, quantidade_lote, peso_lote, observacao).fetchval()
            if not lote_id:
                raise Exception("Falha crítica: O banco de dados não retornou o ID do novo lote.")
            sql_insert_associacao = "INSERT INTO ReceitaProdutoLote (receita_produto_id, lote_id, quantidade_utilizada) VALUES (?, ?, ?)"
            cursor.execute(sql_insert_associacao, receita_produto_id, lote_id, quantidade_utilizada)
            conn.commit() # Este comando agora é o único responsável por salvar.
            flash('Lote adicionado e associado com sucesso!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Erro na transação ao adicionar lote: {e}', 'danger')
        finally:
            conn.close()
    return redirect(url_for('detalhe_receita', receita_id=receita_id))

@app.route('/produtos')
def gerenciar_produtos():
    conn = get_db_conn()
    produtos = []
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ProdutoGlobal ORDER BY nome")
        produtos = cursor.fetchall()
        conn.close()
    return render_template('gerenciar_produtos.html', produtos=produtos)

@app.route('/produtos/novo', methods=['POST'])
def adicionar_produto_global():
    numero_produto = request.form['numero_produto']
    nome = request.form['nome']
    conn = get_db_conn()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO ProdutoGlobal (numero_produto, nome) VALUES (?, ?)",
                           numero_produto, nome)
            conn.commit()
            flash('Novo produto global adicionado com sucesso!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Erro ao adicionar produto global: {e}', 'danger')
        finally:
            conn.close()
    return redirect(url_for('gerenciar_produtos'))

if __name__ == '__main__':
    app.run(debug=True)