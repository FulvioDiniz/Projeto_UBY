import pyodbc
import sys
import os
import time
from datetime import datetime


# --- INÍCIO DA CORREÇÃO PARA EXECUÇÃO DIRETA ---
# Adiciona o diretório raiz do projeto ('python_automacao') ao path do Python.
# Isso permite que o script encontre as pastas 'app' e 'config' ao ser executado diretamente.
try:
    # Pega o caminho do diretório onde este script está (Reatores)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Volta um nível no diretório para chegar na pasta raiz do projeto ('python_automacao')
    project_root = os.path.dirname(current_dir)
    # Adiciona a pasta raiz ao início do path do sistema, se ainda não estiver lá.
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
except NameError:
    # Fallback para ambientes onde __file__ não está definido
    sys.path.insert(0, '.')
# --- FIM DA CORREÇÃO ---


# Agora os imports vão funcionar corretamente
from app.clp import *
from config.settings import get_plc_ip



# --- CONFIGURAÇÃO E CONEXÃO COM BANCO DE DADOS ---
# (As mesmas funções que você já criou)
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

# --- FUNÇÕES DE CONSULTA AO BANCO (Suas novas funções) ---

def get_receita_com_lotes_atribuidos(cursor, receita_id: int) -> dict | None:
    """
    Busca os detalhes de uma receita, incluindo APENAS os lotes que foram
    especificamente ATRIBUÍDOS/VINCULADOS a cada produto da receita.
    """
    # CORREÇÃO 2: A consulta foi TOTALMENTE substituída pela consulta correta.
    query = """
    	   
	    SELECT
        r.receita_id,
        r.nome_receita,
        rp.receita_produto_id,
        pg.produto_id,
        pg.numero_produto,
        pg.nome AS produto_nome,
        rp.quantidade_total AS quantidade_necessaria,
        l.lote_id,
        l.quantidade_lote,
        l.peso_lote,
        l.observacao_lote,
		l.peso_lote,
        rpl.quantidade_utilizada -- Informação crucial da tabela de vínculo
    FROM
        Receita r
    JOIN
        ReceitaProduto rp ON r.receita_id = rp.receita_id
    JOIN
        -- Este é o JOIN que filtra APENAS os lotes vinculados
        ReceitaProdutoLote rpl ON rp.receita_produto_id = rpl.receita_produto_id
    JOIN
        Lote l ON rpl.lote_id = l.lote_id
    JOIN
        ProdutoGlobal pg ON l.produto_id = pg.produto_id
    WHERE
        r.receita_id = ?
    ORDER BY
        pg.produto_id;
    """
    try:
        cursor.execute(query, receita_id)
        rows = cursor.fetchall()
        if not rows:
            # Se não houver lotes vinculados, a consulta não retornará nada.
            # Você pode querer um tratamento diferente aqui, como buscar os dados da receita sem lotes.
            return None

        receita_info = {
            'receita_id': rows[0].receita_id,
            'nome_receita': rows[0].nome_receita,
            'produtos': {}
        }
        
        for row in rows:
            if row.produto_id not in receita_info['produtos']:
                receita_info['produtos'][row.produto_id] = {
                    'produto_id': row.produto_id,
                    'numero_produto': row.numero_produto,
                    'receita_produto_id': row.receita_produto_id,
                    'nome_produto': row.produto_nome,
                    'quantidade_necessaria': row.quantidade_necessaria,
                    # CORREÇÃO 3: A lista agora se chama 'lotes_atribuidos' para maior clareza.
                    'lotes_atribuidos': []
                }
            
            # Como a consulta agora usa JOIN (e não LEFT JOIN), o lote_id sempre existirá.
            receita_info['produtos'][row.produto_id]['lotes_atribuidos'].append({
                'lote_id': row.lote_id,
                'quantidade_lote': row.quantidade_lote,
                'peso_lote': row.peso_lote,
                'observacao': row.observacao_lote,
                # CORREÇÃO 4: Adicionamos a quantidade específica usada deste lote.
                'quantidade_utilizada': row.quantidade_utilizada
            })
        
        return receita_info

    except pyodbc.Error as e:
        print(f"Erro ao buscar detalhes da receita {receita_id}: {e}")
        return None



def numero_produto_receita(cursor, receita_id: int) -> list | None:
    query = "SELECT TOP 1 produto_numero from Receita where receita_id = ?"
    try:
        cursor.execute(query, receita_id)
        rows = cursor.fetchall()
        if not rows:
            return None
        return rows[0].produto_numero
    except pyodbc.Error as e:
        print(f"Erro ao buscar número do produto da receita {receita_id}: {e}")
        return None

def iniciar_producao(cursor, receita_id: int, observacao: str = None) -> int | None:
    """
    Cria um novo registro na tabela Producao usando a cláusula OUTPUT,
    que é a forma mais robusta de obter o ID recém-criado.
    """

    query = """
    INSERT INTO Producao (receita_id, data_inicio, status_producao, observacao)
    OUTPUT INSERTED.producao_id
    VALUES (?, ?, ?, ?);
    """
    
    try:
        data_inicio = datetime.now()
        status_inicial = 'Iniciada'
        
        # A execução agora retorna um resultado diretamente
        cursor.execute(query, receita_id, data_inicio, status_inicial, observacao)
        
        # O fetchone() irá capturar o valor retornado pela cláusula OUTPUT
        resultado = cursor.fetchone()

        # Adiciona uma verificação para garantir que o resultado não é None
        if resultado:
            producao_id = resultado[0]
            cursor.connection.commit()
            print(f"Produção iniciada com sucesso. ID da Produção: {producao_id}")
            return producao_id
        else:
            # Isso não deveria acontecer com a cláusula OUTPUT, mas é uma proteção
            print("Erro crítico: A instrução INSERT com OUTPUT não retornou um ID.")
            cursor.connection.rollback()
            return None

    except pyodbc.Error as e:
        cursor.connection.rollback()
        print(f"Erro ao iniciar produção para a receita {receita_id}: {e}")
        return None


def get_peso_total_previsto_por_id(cursor: pyodbc.Cursor, receita_id: int) -> float | None:
    """
    Busca no banco de dados o peso total PREVISTO (planejado) de uma receita,
    usando o seu ID.

    Args:
        cursor (pyodbc.Cursor): O cursor da conexão com o banco de dados.
        receita_id (int): O ID exato da receita a ser consultada.

    Returns:
        float: O peso total previsto calculado. Retorna 0.0 se a receita não for encontrada.
        None: Em caso de erro na consulta.
    """
    # A query agora filtra pela chave primária (r.receita_id), que é mais eficiente.
    query = """
        SELECT
            SUM(rp.quantidade_total)
        FROM
            Receita r
        JOIN
            ReceitaProduto rp ON r.receita_id = rp.receita_id
        WHERE
            r.receita_id = ?;
    """
    
    try:
        # Executa a query passando o ID da receita como parâmetro
        cursor.execute(query, receita_id)
        resultado = cursor.fetchone()

        # Verifica se o resultado não é nulo e se o valor dentro dele também não é
        if resultado and resultado[0] is not None:
            return int(resultado[0])
        else:
            # Se a receita não tiver produtos ou não for encontrada, o peso total é 0
            return 0

    except pyodbc.Error as e:
        print(f"Ocorreu um erro ao consultar o peso previsto da receita com ID {receita_id}: {e}")
        return None
    
def update_producao(cursor, receita_id: int, observacao: str = None) -> int | None:
    """
    Cria um novo registro na tabela Producao usando a cláusula OUTPUT,
    que é a forma mais robusta de obter o ID recém-criado.
    """

    query = """
    INSERT INTO Producao (receita_id, data_inicio, status_producao, observacao)
    OUTPUT INSERTED.producao_id
    VALUES (?, ?, ?, ?);
    """
    
    try:
        data_inicio = datetime.now()
        status_inicial = 'Iniciada'
        
        # A execução agora retorna um resultado diretamente
        cursor.execute(query, receita_id, data_inicio, status_inicial, observacao)
        
        # O fetchone() irá capturar o valor retornado pela cláusula OUTPUT
        resultado = cursor.fetchone()

        # Adiciona uma verificação para garantir que o resultado não é None
        if resultado:
            producao_id = resultado[0]
            cursor.connection.commit()
            print(f"Produção iniciada com sucesso. ID da Produção: {producao_id}")
            return producao_id
        else:
            # Isso não deveria acontecer com a cláusula OUTPUT, mas é uma proteção
            print("Erro crítico: A instrução INSERT com OUTPUT não retornou um ID.")
            cursor.connection.rollback()
            return None

    except pyodbc.Error as e:
        cursor.connection.rollback()
        print(f"Erro ao iniciar produção para a receita {receita_id}: {e}")
        return None

def registrar_pesagem(cursor, producao_id: int, etapa: str, peso: float, responsavel: str,
                      receita_produto_id: int, lote_id: int):
    """
    Registra uma pesagem e o uso do lote associado.
    """
    query_uso_lote = "INSERT INTO ReceitaProdutoLote (receita_produto_id, lote_id, quantidade_utilizada) VALUES (?, ?, ?);"
    query_pesagem = "INSERT INTO ProducaoPesagem (producao_id, etapa_processo, peso, data_pesagem, responsavel) VALUES (?, ?, ?, ?, ?);"
    
    try:
        # 1. Registrar o uso do lote
        cursor.execute(query_uso_lote, receita_produto_id, lote_id, peso)

        # 2. Registrar a pesagem
        data_pesagem = datetime.now()
        cursor.execute(query_pesagem, producao_id, etapa, peso, data_pesagem, responsavel)
        
        # O commit será feito pela função que chama esta, após todas as pesagens.
        print(f"Registro de pesagem para a etapa '{etapa}' preparado.")
    
    except pyodbc.Error as e:
        # Levanta uma exceção para que a transação seja revertida pela função chamadora.
        raise Exception(f"Erro ao registrar pesagem para receita_produto_id {receita_produto_id} e lote {lote_id}: {e}")
    
    
    
def get_pesos_por_produto(cursor: pyodbc.Cursor, receita_id: int):
    """
    Busca os pesos previstos para cada produto de uma receita e os retorna
    em um dicionário para fácil alinhamento.

    Args:
        cursor (pyodbc.Cursor): O cursor da conexão com o banco de dados.
        receita_id (int): O ID da receita a ser consultada.

    Returns:
        Dict[str, float]: Um dicionário mapeando 'numero_produto' para 'peso_previsto'.
                          Ex: {'30060006': 500.0, '30070010': 120.5}
        None: Em caso de erro na consulta.
    """
    # Esta é a sua consulta, com o ID parametrizado para segurança
    query = """
        SELECT
            rp.quantidade_total AS peso_previsto
        FROM
            Receita r
        JOIN
            ReceitaProduto rp ON r.receita_id = rp.receita_id
        JOIN
            ProdutoGlobal pg ON rp.produto_id = pg.produto_id
        WHERE
            r.receita_id = ?;
    """
    
    try:
        cursor.execute(query, receita_id)
        rows = cursor.fetchall()
        
        # Cria um dicionário para mapear o número do produto ao seu peso
        pesos_mapeados = {
            str(row.numero_produto): float(row.peso_previsto) 
            for row in rows
        }
        
        return pesos_mapeados

    except pyodbc.Error as e:
        print(f"Ocorreu um erro ao buscar os pesos da receita com ID {receita_id}: {e}")
        return None

# --- LÓGICA PRINCIPAL DE INTERAÇÃO COM CLP (Seu código antigo, agora refatorado) ---

# VERSÃO CORRIGIDA

def processar_e_enviar_receita_para_clp(plc: LogixDriver, cursor, receita_id: int, reator_id: int) -> bool:
    """
    Busca os detalhes da receita com seus lotes ATRIBUÍDOS e envia para o CLP.
    AGORA CORRIGIDA PARA USAR A CONEXÃO 'plc' EXISTENTE.
    """
    # REMOVIDO: A linha abaixo foi removida pois agora recebemos o objeto 'plc' conectado.
    # PLC_IP = get_plc_ip()
    
    detalhes_receita = get_receita_com_lotes_atribuidos(cursor, receita_id)
    
    if not detalhes_receita:
        print(f"Não foi encontrada nenhuma receita com ID {receita_id} ou ela não possui lotes atribuídos.")
        return False

    try:
        numero_produto = numero_produto_receita(cursor, receita_id)
        # ALTERADO: Todas as chamadas agora usam 'plc' em vez de 'PLC_IP' e 'reator_id' em vez de '1'.
        set_valor_receita_produto_id_to_clp(plc, reator_id, numero_produto)
        
        # Envia nome da receita
        set_Recipe_Name_to_clp(plc, detalhes_receita['nome_receita'], reator_id)
        
        # Envia o peso total previsto da receita inteira
        peso_total_Previsto = get_peso_total_previsto_por_id(cursor, receita_id)
        if peso_total_Previsto > 0:
            print(f"Peso total previsto para a receita {receita_id}: {peso_total_Previsto} kg")
            set_value_product_predicted_to_plc(plc, int(peso_total_Previsto), reator_id)

        total_lotes_na_receita = sum(len(p['lotes_atribuidos']) for p in detalhes_receita['produtos'].values())
        if total_lotes_na_receita == 0: total_lotes_na_receita = 1

        load_acumulado = 0

        # Itera sobre os produtos da receita
        for i_produto, (produto_id, produto) in enumerate(detalhes_receita['produtos'].items()):
            indice_clp = i_produto
            
            print(f"\nProcessando Produto ID {produto_id} ({produto['nome_produto']}) no Índice CLP {indice_clp}")
            
            # Envia o peso previsto deste produto específico
            peso_previsto_do_produto = produto['quantidade_necessaria']
            set_quantidade_produto_to_clp(plc, reator_id, indice_clp, peso_previsto_do_produto)

            load_acumulado += len(produto['lotes_atribuidos'])
            percentual_carga = (load_acumulado / total_lotes_na_receita) * 100
            set_value_bar_loading_to_plc(plc, int(percentual_carga))
            print(f"Progresso: {int(percentual_carga)}%")

            todos_os_lotes_do_produto = produto['lotes_atribuidos']

            if len(todos_os_lotes_do_produto) > 4:
                print(f"AVISO: Produto '{produto['nome_produto']}' tem {len(todos_os_lotes_do_produto)} lotes. Apenas os 4 primeiros serão enviados.")

            pacote_de_lotes = todos_os_lotes_do_produto[:4]
            
            if not pacote_de_lotes:
                print("Produto sem lotes atribuídos. Enviando zeros para o CLP.")
                pesos = [0] * 4
                textos = [""] * 4
            else:
                pesos = [lote['peso_lote'] for lote in pacote_de_lotes] + [0] * (4 - len(pacote_de_lotes))
                textos = [lote['observacao'] for lote in pacote_de_lotes] + [""] * (4 - len(pacote_de_lotes))

            print(f"Enviando {len(pacote_de_lotes)} lote(s) para o produto no índice CLP {indice_clp}. Pesos: {pesos}")
            
            # Envia o pacote único de lotes para o CLP usando o índice correto
            # CORRIGIDO: Agora passa 'reator_id' corretamente
            set_lotes_peso_from_clp(plc, indice_clp, *pesos, reator_id)
            set_lotes_TEXTO_from_clp(plc, indice_clp, *textos, reator_id)

        print("\nEnvio da receita para o CLP concluído com sucesso.")
        return True

    except Exception as e:
        print(f"Ocorreu um erro ao enviar dados para o CLP: {e}")
        return False
    
def registrar_uma_pesagem(cursor, producao_id: int, etapa: str, peso, responsavel: str):
    """
    Insere um único registro de pesagem na tabela ProducaoPesagem.
    """
    sql_query = """
    INSERT INTO ProducaoPesagem (producao_id, etapa_processo, peso, data_pesagem, responsavel)
    VALUES (?, ?, ?, GETDATE(), ?);
    """
    try:
        cursor.execute(sql_query, producao_id, etapa, peso, responsavel)
        print(f"  -> Registro de pesagem para '{etapa}' com peso {peso} kg adicionado à transação.")
    except Exception as e:
        print(f"ERRO ao tentar executar o INSERT na tabela ProducaoPesagem: {e}")
        # Lança o erro para que a transação principal seja revertida (rollback).
        raise e
    
def registrar_dados_finais_da_producao(plc: LogixDriver, cursor, producao_id: int, receita_id: int, reator_id: int):
    """
    Busca os pesos medidos do CLP para cada produto/lote e os registra no banco de dados.
    Esta versão integra a lógica de leitura do CLP para maior clareza e robustez.
    """
    print("Iniciando o registro dos dados finais de pesagem...")
    
    try:
        # Busca a estrutura da receita para saber quais lotes foram enviados ao CLP
        detalhes_receita = get_receita_com_lotes_atribuidos(cursor, receita_id)
        if not detalhes_receita:
            raise Exception(f"Não foi possível encontrar a receita {receita_id} para salvar os dados.")

        # Itera sobre os produtos da receita, na mesma ordem em que foram enviados ao CLP
        for i_produto, (produto_id, produto) in enumerate(detalhes_receita['produtos'].items()):
            indice_clp = i_produto
            nome_produto = produto['nome_produto']
            receita_produto_id = produto['receita_produto_id']

            # Pega a lista de lotes que foram efetivamente enviados para este produto (no máximo 4)
            lotes_enviados = produto['lotes_atribuidos'][:4]
            
            if not lotes_enviados:
                print(f"\nProduto '{nome_produto}' não teve lotes enviados, pulando para o próximo.")
                continue

            print(f"\nBuscando pesos do CLP para o produto '{nome_produto}' (Índice CLP: {indice_clp})")

            # Monta a lista de tags de peso para ler do CLP para este produto específico
            tags_pesos_a_ler = [f'ERP_REATOR{reator_id}.OUT_INFOR_LOTE[{indice_clp}].PESO_{i+1}' for i in range(4)]
            
            # Lê as 4 tags de peso para este produto de uma só vez
            resultados_pesos = plc.read(*tags_pesos_a_ler)
            pesos_medidos = [res.value if res else 0.0 for res in resultados_pesos]

            print(f"  Pesos medidos recebidos do CLP: {pesos_medidos}")

            # Associa cada peso medido ao seu lote correspondente e chama a função de registro
            for i, lote in enumerate(lotes_enviados):
                peso_medido = pesos_medidos[i]
                
                # Só registra se o peso for um valor válido e maior que zero
                if peso_medido is not None and peso_medido > 0:
                    etapa_descritiva = f"Pesagem de {nome_produto} - Lote Obs: {lote['observacao']}"
                    
                    # Chama a função auxiliar para fazer o INSERT no banco
                    registrar_uma_pesagem(
                        cursor=cursor,
                        producao_id=producao_id,
                        etapa=etapa_descritiva,
                        peso=peso_medido,
                        responsavel="Sistema de Automação"
                    )

        # Se o loop de todos os produtos terminou sem erros, atualiza o status final da produção
        print("\nAtualizando status da produção para 'Finalizada'.")
        cursor.execute("UPDATE Producao SET status_producao = ?, data_fim = GETDATE() WHERE producao_id = ?;", "Finalizada", producao_id)

        # Efetiva todas as mudanças no banco de dados
        cursor.connection.commit()
        print("\nSUCESSO! Todos os dados de pesagem e o status da produção foram salvos no banco de dados.")
        return True

    except Exception as e:
        # Se qualquer erro ocorrer em qualquer etapa, reverte todas as operações feitas no banco
        print(f"ERRO GERAL AO SALVAR DADOS DA PRODUÇÃO: {e}. A transação foi revertida (rollback).")
        cursor.connection.rollback()
        return False



def Reator1():
    """
    Loop principal que monitora o CLP para iniciar e finalizar produções,
    utilizando uma conexão persistente e uma lógica de espera robusta.
    """
    PLC_IP = get_plc_ip()
    SLOT_DO_CLP = 0
    caminho_conexao = f'{PLC_IP}/1/{SLOT_DO_CLP}'
    plc = None

    while True:
        try:
            # --- Bloco de Gerenciamento da Conexão ---
            if plc is None or not plc.connected:
                print(f"Conectando ao CLP via: {caminho_conexao}...")
                if plc: plc.close()
                plc = LogixDriver(caminho_conexao, init_program_tags=False)
                plc.open()
                print(f"Conectado com sucesso ao CLP: {plc.info.get('product_name', 'N/A')}")

            # --- Início da Lógica de Produção ---
            if validador_send_lote(plc, 1):
                cursor = Conexao_SQLSERVER(DB_CONFIG)
                if not cursor:
                    print("Falha ao conectar ao banco de dados. O processo não pode continuar.")
                    time.sleep(10)
                    continue

                try:
                    receita_id = get_Receitaid_from_clp(plc, 1)
                    print(f"CLP solicitou o processamento da receita ID: {receita_id}")
                    
                    producao_id_atual = iniciar_producao(cursor, receita_id, "Produção iniciada pelo Reator 1")
                    
                    if not producao_id_atual:
                        # Se não conseguir criar o registro no banco, sinaliza falha e para o ciclo.
                        raise Exception(f"Falha ao iniciar a produção para a receita {receita_id}")

                    # --- CAMINHO DE SUCESSO ---
                    open_pop_up_loading_to_plc(plc, 1, True)
                    set_visble_send_lote_to_clp(plc, 1, True)

                    sucesso_envio = processar_e_enviar_receita_para_clp(plc, cursor, receita_id, 1)

                    if sucesso_envio:
                        # --- INÍCIO DO BLOCO DE ESPERA (REVISADO) ---
                        validador_set_bit_enviado_to_plc(plc, 1, True)
                        time.sleep(1)
                        validador_set_bit_enviado_to_plc(plc, 1, False)
                        
                        open_pop_up_loading_to_plc(plc, 1, False)
                        set_value_bar_loading_to_plc(plc, 0)
                        set_validador_send_lote_concluido(plc, 1, False)

                        # Reset preventivo dos bits de controle ANTES de começar a esperar.
                        #print("Resetando bits de controle do CLP antes de iniciar a espera...")
                        #set_finaliza_receita(plc, 1, False)
                        # Nota: Você precisa de uma função para resetar o bit de exclusão também.
                        # set_exclusao_receita_to_clp(plc, 1, False) # <- Você precisará criar esta função.

                        print("Aguardando finalização ou cancelamento da receita pelo CLP...")
                        max_attempts = 300000000000  # ~5 minutos
                        processo_concluido = False
                        
                        for i in range(max_attempts):
                            print(f"Loop de espera [Iteração {i+1}/{max_attempts}]...")
                            
                            # Verifica o bit de finalização do CLP
                            if get_finaliza_receita(plc, 1):
                                print(">>> SINAL DE FINALIZAÇÃO RECEBIDO! <<<")
                                
                                # --- CHAMADA CORRIGIDA AQUI ---
                                # Agora passando todos os 5 argumentos necessários
                                registrar_dados_finais_da_producao(plc, cursor, producao_id_atual, receita_id, 1)                                
                                set_finaliza_receita(plc, 1, False) # Limpa o bit por segurança
                                processo_concluido = True
                                break # Sai do loop de espera
                            
                            # Verifica o bit de cancelamento do operador
                            if get_exclusao_receita_to_clp(plc, 1):
                                print(">>> SINAL DE CANCELAMENTO RECEBIDO! <<<")
                                update_producao(cursor, receita_id, "Produção cancelada pelo operador")
                                processo_concluido = True
                                break # Sai do loop de espera
                            
                            time.sleep(1) # Espera 1 segundo antes da p
                        
                        if not processo_concluido:
                            print("TIMEOUT: Processo da receita excedeu o tempo limite de espera.")
                        
                        # --- FIM DO BLOCO DE ESPERA (REVISADO) ---

                    else: # Falha no processar_e_enviar_receita_para_clp
                        raise Exception("Falha ao processar e enviar receita para o CLP")

                except Exception as e:
                    print(f"ERRO durante o processamento da receita: {e}")
                    # Rotina de falha: avisa o CLP
                    validador_falha_set_bit_enviado_to_plc(plc, 1, True)
                    time.sleep(5)
                    validador_falha_set_bit_enviado_to_plc(plc, 1, False)
                    # Garante que a solicitação do CLP seja limpa para evitar loops de erro
                    set_validador_send_lote_concluido(plc, 1, False)

                finally:
                    if cursor:
                        cursor.close()
                    print("\nConexão com o banco fechada. Aguardando próxima solicitação...")
            
            # Pausa do loop principal
            time.sleep(1)

        except PycommError as e:
            print(f"ERRO DE COMUNICAÇÃO COM O CLP: {e}. Tentando reconectar em 10 segundos...")
            if plc: plc.close()
            plc = None
            time.sleep(10)
        
        except Exception as e:
            print(f"Ocorreu um erro inesperado no loop principal: {e}")
            time.sleep(10)

if __name__ == "__main__":
    print("Iniciando monitoramento do Reator 1...")
    Reator1()