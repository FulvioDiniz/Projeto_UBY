import pyodbc
import sys
import os
from datetime import datetime

# --- CONFIGURAÇÃO E CONEXÃO (sem alterações) ---

# Adiciona o diretório "python_automacao" ao sys.path.
# Nota: Verifique se este caminho está correto para o seu ambiente.
try:
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)
    # Importa as classes (assumindo que elas existem)
    # from Variaveis_Teste.Receita import Receita2, Produto, Lote
except (NameError, ImportError):
    # Se __file__ não estiver definido (ex: em um notebook) ou o módulo não for encontrado.
    print("Aviso: Não foi possível configurar o sys.path ou importar as classes customizadas.")
    pass

server = 'FULVIO\\FULVIO'
database = 'Banco reformulado'
username = 'sa'
password = '123456'

DB_CONFIG = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password}'
)

def Conexao_SQLSERVER(db_config):
    """Estabelece a conexão com o banco de dados SQL Server."""
    try:
        cnxn = pyodbc.connect(db_config)
        cursor = cnxn.cursor()
        print("Conexão estabelecida com sucesso!")
        return cursor
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"Erro ao conectar ao SQL Server. SQLSTATE: {sqlstate}")
        print(ex)
        return None

# --- FUNÇÕES RECONSTRUÍDAS ---

def get_numeros_de_produto_da_receita(cursor, receita_id: int) -> list[int] | None:
    """
    Consulta e retorna uma lista com todos os números de produto (numero_produto) 
    associados a uma receita específica.

    Args:
        cursor: Um objeto cursor de banco de dados conectado.
        receita_id (int): O ID da receita a ser consultada.

    Returns:
        list[int]: Uma lista contendo os números de produto. Retorna lista vazia se não houver.
        None: Se ocorrer um erro na consulta.
    """
    # CORREÇÃO: A query original buscava `r.produto_numero`, que é um campo de contagem na
    # tabela Receita. A query correta busca `pg.numero_produto` da tabela ProdutoGlobal.
    query = """
    SELECT DISTINCT
        pg.numero_produto
    FROM [ReceitaProduto] rp
    JOIN [ProdutoGlobal] pg ON rp.produto_id = pg.produto_id
    WHERE rp.receita_id = ?
    ORDER BY pg.numero_produto;
    """
    try:
        cursor.execute(query, receita_id)
        # Extrai o primeiro elemento (numero_produto) de cada tupla retornada.
        return [row[0] for row in cursor.fetchall()]
    except pyodbc.Error as e:
        print(f"ERRO ao consultar os números de produto para a receita {receita_id}: {e}")
        return None

def get_receita_com_lotes_disponiveis(cursor, receita_id: int) -> dict | None:
    """
    Busca os detalhes de uma receita, incluindo todos os LOTES DISPONÍVEIS para cada
    produto da receita.
    
    NOTA: Esta função mostra todos os lotes cadastrados para um produto, não necessariamente
    os lotes que serão/foram usados em uma produção específica.

    Args:
        cursor: Cursor de banco de dados conectado.
        receita_id (int): O ID da receita.

    Returns:
        dict: Um dicionário representando a receita, seus produtos e todos os lotes
              disponíveis para cada produto.
        None: Se a receita não for encontrada ou ocorrer um erro.
    """
    query = """
    SELECT 
        r.receita_id,
        r.nome_receita,
        rp.receita_produto_id, -- ID da ligação receita-produto, útil para outras operações
        pg.produto_id,
        pg.numero_produto,
        pg.nome AS produto_nome,
        rp.quantidade_total AS quantidade_necessaria,
        l.lote_id,
        l.quantidade_lote,
        l.peso_lote,
        l.observacao_lote
    FROM [Receita] r
    JOIN [ReceitaProduto] rp ON r.receita_id = rp.receita_id
    JOIN [ProdutoGlobal] pg ON rp.produto_id = pg.produto_id
    LEFT JOIN [Lote] l ON pg.produto_id = l.produto_id -- LEFT JOIN para incluir produtos sem lote
    WHERE r.receita_id = ?
    ORDER BY pg.numero_produto, l.lote_id;
    """
    try:
        cursor.execute(query, receita_id)
        rows = cursor.fetchall()
        if not rows:
            return None

        # Organiza os dados em uma estrutura de dicionário aninhado
        receita_info = {
            'receita_id': rows[0].receita_id,
            'nome_receita': rows[0].nome_receita,
            'produtos': {}
        }
        
        for row in rows:
            if row.numero_produto not in receita_info['produtos']:
                receita_info['produtos'][row.numero_produto] = {
                    'produto_id': row.produto_id,
                    'receita_produto_id': row.receita_produto_id,
                    'nome_produto': row.produto_nome,
                    'quantidade_necessaria': row.quantidade_necessaria,
                    'lotes_disponiveis': []
                }
            
            if row.lote_id: # Adiciona o lote apenas se ele existir
                receita_info['produtos'][row.numero_produto]['lotes_disponiveis'].append({
                    'lote_id': row.lote_id,
                    'quantidade_lote': row.quantidade_lote,
                    'peso_lote': row.peso_lote,
                    'observacao': row.observacao_lote
                })
        
        return receita_info

    except pyodbc.Error as e:
        print(f"Erro ao buscar detalhes da receita {receita_id}: {e}")
        return None

# --- NOVAS FUNÇÕES PARA GERENCIAR A PRODUÇÃO ---

def iniciar_producao(cursor, receita_id: int, observacao: str = None) -> int | None:
    """
    Cria um novo registro na tabela Producao para marcar o início de uma produção.

    Args:
        cursor: Cursor de banco de dados conectado.
        receita_id (int): O ID da receita que está sendo produzida.
        observacao (str, optional): Uma observação sobre a produção.

    Returns:
        int: O ID da produção (`producao_id`) recém-criada.
        None: Se ocorrer um erro.
    """
    query = """
    INSERT INTO Producao (receita_id, data_inicio, status_producao, observacao)
    VALUES (?, ?, ?, ?);
    SELECT SCOPE_IDENTITY(); -- Retorna o último ID inserido nesta sessão
    """
    try:
        data_inicio = datetime.now()
        status_inicial = 'Iniciada'
        
        cursor.execute(query, receita_id, data_inicio, status_inicial, observacao)
        producao_id = cursor.fetchone()[0]
        cursor.connection.commit()
        
        print(f"Produção iniciada com sucesso. ID da Produção: {producao_id}")
        return producao_id
    except pyodbc.Error as e:
        cursor.connection.rollback()
        print(f"Erro ao iniciar produção para a receita {receita_id}: {e}")
        return None

def registrar_uso_lote(cursor, receita_produto_id: int, lote_id: int, quantidade_utilizada: float):
    """
    Registra na tabela ReceitaProdutoLote qual lote foi usado e em que quantidade
    para um determinado item da receita.

    Args:
        cursor: Cursor de banco de dados conectado.
        receita_produto_id (int): O ID da linha na tabela ReceitaProduto (vínculo receita-produto).
        lote_id (int): O ID do lote que foi utilizado.
        quantidade_utilizada (float): A quantidade do lote que foi usada.
    """
    query = """
    INSERT INTO ReceitaProdutoLote (receita_produto_id, lote_id, quantidade_utilizada)
    VALUES (?, ?, ?);
    """
    try:
        cursor.execute(query, receita_produto_id, lote_id, quantidade_utilizada)
        # O commit será feito pela função que orquestra o processo (ex: registrar_pesagem)
        print(f"Uso do lote {lote_id} registrado para receita_produto_id {receita_produto_id}.")
    except pyodbc.Error as e:
        raise Exception(f"Erro ao registrar uso do lote {lote_id}: {e}")

def registrar_pesagem(cursor, producao_id: int, etapa: str, peso: float, responsavel: str,
                      receita_produto_id: int, lote_id: int):
    """
    Função completa que registra uma pesagem na tabela ProducaoPesagem e também
    associa o lote utilizado ao item da receita na tabela ReceitaProdutoLote.

    Args:
        cursor: Cursor de banco de dados conectado.
        producao_id (int): O ID da produção em andamento.
        etapa (str): Descrição da etapa do processo (ex: "Pesagem Produto X").
        peso (float): O peso medido.
        responsavel (str): Quem realizou a pesagem.
        receita_produto_id (int): O ID do vínculo receita-produto (de ReceitaProduto).
        lote_id (int): O ID do lote de onde o material foi retirado.
    """
    # A quantidade utilizada é o próprio peso medido nesta etapa.
    quantidade_utilizada = peso
    
    try:
        # 1. Registrar o uso do lote
        registrar_uso_lote(cursor, receita_produto_id, lote_id, quantidade_utilizada)

        # 2. Registrar a pesagem em si
        query_pesagem = """
        INSERT INTO ProducaoPesagem (producao_id, etapa_processo, peso, data_pesagem, responsavel)
        VALUES (?, ?, ?, ?, ?);
        """
        data_pesagem = datetime.now()
        cursor.execute(query_pesagem, producao_id, etapa, peso, data_pesagem, responsavel)
        
        # 3. Finalizar a transação
        cursor.connection.commit()
        print(f"Pesagem de {peso}kg para a etapa '{etapa}' registrada com sucesso na produção {producao_id}.")
    
    except Exception as e:
        cursor.connection.rollback()
        print(f"ERRO GERAL AO REGISTRAR PESAGEM: {e}. A transação foi revertida.")


# --- MAIN - Exemplo de uso das novas funções ---
if __name__ == "__main__":
    cursor = Conexao_SQLSERVER(DB_CONFIG)
    if cursor:
        try:
            receita_id_teste = 20020111 # Use um ID de receita válido do seu banco

            print("\n--- 1. Buscando números de produto da receita ---")
            numeros_produto = get_numeros_de_produto_da_receita(cursor, receita_id_teste)
            if numeros_produto:
                print(f"Números de produto para a receita {receita_id_teste}: {numeros_produto}")
            else:
                print(f"Nenhum produto encontrado para a receita {receita_id_teste}.")

            print("\n--- 2. Buscando detalhes da receita e lotes disponíveis ---")
            detalhes_receita = get_receita_com_lotes_disponiveis(cursor, receita_id_teste)
            if detalhes_receita:
                print(f"Nome da Receita: {detalhes_receita['nome_receita']}")
                for np, produto in detalhes_receita['produtos'].items():
                    print(f"  - Produto {np} ({produto['nome_produto']}):")
                    print(f"    ID do Vínculo (receita_produto_id): {produto['receita_produto_id']}")
                    print(f"    Quantidade Necessária: {produto['quantidade_necessaria']}")
                    print(f"    Lotes disponíveis: {len(produto['lotes_disponiveis'])}")
                    if produto['lotes_disponiveis']:
                        primeiro_lote = produto['lotes_disponiveis'][0]
                        print(f"      -> Exemplo Lote ID: {primeiro_lote['lote_id']}, Qtd: {primeiro_lote['quantidade_lote']}")
            
            print("\n--- 3. Simulando um processo de produção e pesagem ---")
            # Inicia uma nova produção para a receita
            producao_id_atual = iniciar_producao(cursor, receita_id_teste, observacao="Produção de teste via script")

            if producao_id_atual and detalhes_receita:
                # Vamos simular a pesagem do primeiro produto da receita, usando seu primeiro lote disponível
                primeiro_produto_np = next(iter(detalhes_receita['produtos'])) # Pega o número do primeiro produto
                primeiro_produto_info = detalhes_receita['produtos'][primeiro_produto_np]
                
                if primeiro_produto_info['lotes_disponiveis']:
                    receita_produto_id_pesagem = primeiro_produto_info['receita_produto_id']
                    lote_a_ser_usado = primeiro_produto_info['lotes_disponiveis'][0]
                    lote_id_pesagem = lote_a_ser_usado['lote_id']
                    
                    # Simula a pesagem de 5.5 kg deste produto
                    peso_medido = 5.5
                    
                    registrar_pesagem(
                        cursor=cursor,
                        producao_id=producao_id_atual,
                        etapa=f"Pesagem de {primeiro_produto_info['nome_produto']}",
                        peso=peso_medido,
                        responsavel="Sistema de Automação",
                        receita_produto_id=receita_produto_id_pesagem,
                        lote_id=lote_id_pesagem
                    )
                else:
                    print(f"Produto {primeiro_produto_np} não possui lotes disponíveis para simular a pesagem.")
        
        finally:
            print("\nFechando conexão.")
            cursor.close()
            
            
            
            
            
            
            
        