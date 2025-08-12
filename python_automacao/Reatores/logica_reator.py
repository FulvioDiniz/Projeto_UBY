import pyodbc
import sys
import os
import time
from datetime import datetime
from threading import Event
from threading import Event, Lock

# Adiciona o diretório raiz ao path para encontrar os módulos app e config
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
except NameError:
    sys.path.insert(0, '.')

from app.clp import *
from config.settings import get_plc_ip

# --- CONFIGURAÇÃO E FUNÇÕES DE BANCO DE DADOS ---
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
        # autocommit=False é importante para controlar transações manualmente
        cnxn = pyodbc.connect(db_config, autocommit=False)
        cursor = cnxn.cursor()
        print("Conexão com o banco de dados estabelecida com sucesso!")
        return cursor
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"Erro ao conectar ao SQL Server. SQLSTATE: {sqlstate}")
        print(ex)
        return None

def get_receita_com_lotes_atribuidos(cursor, receita_id: int) -> dict | None:
    """
    Busca os detalhes de uma receita, incluindo APENAS os lotes que foram
    especificamente ATRIBUÍDOS/VINCULADOS a cada produto da receita.
    """
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
        rpl.quantidade_utilizada
    FROM
        Receita r
    JOIN
        ReceitaProduto rp ON r.receita_id = rp.receita_id
    JOIN
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
                    'lotes_atribuidos': []
                }
            
            receita_info['produtos'][row.produto_id]['lotes_atribuidos'].append({
                'lote_id': row.lote_id,
                'quantidade_lote': row.quantidade_lote,
                'peso_lote': row.peso_lote,
                'observacao': row.observacao_lote,
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
        return rows[0].produto_numero if rows else None
    except pyodbc.Error as e:
        print(f"Erro ao buscar número do produto da receita {receita_id}: {e}")
        return None

def iniciar_producao(cursor, receita_id: int, observacao: str = None) -> int | None:
    query = """
    INSERT INTO Producao (receita_id, data_inicio, status_producao, observacao)
    OUTPUT INSERTED.producao_id
    VALUES (?, GETDATE(), ?, ?);
    """
    try:
        status_inicial = 'Iniciada'
        cursor.execute(query, receita_id, status_inicial, observacao)
        resultado = cursor.fetchone()
        if resultado:
            producao_id = resultado[0]
            cursor.connection.commit()
            print(f"Produção iniciada com sucesso. ID da Produção: {producao_id}")
            return producao_id
        else:
            print("Erro crítico: A instrução INSERT com OUTPUT não retornou um ID.")
            cursor.connection.rollback()
            return None
    except pyodbc.Error as e:
        cursor.connection.rollback()
        print(f"Erro ao iniciar produção para a receita {receita_id}: {e}")
        return None

def get_peso_total_previsto_por_id(cursor: pyodbc.Cursor, receita_id: int) -> float | None:
    query = """
        SELECT SUM(rp.quantidade_total)
        FROM Receita r
        JOIN ReceitaProduto rp ON r.receita_id = rp.receita_id
        WHERE r.receita_id = ?;
    """
    try:
        cursor.execute(query, receita_id)
        resultado = cursor.fetchone()
        return int(resultado[0]) if resultado and resultado[0] is not None else 0
    except pyodbc.Error as e:
        print(f"Ocorreu um erro ao consultar o peso previsto da receita com ID {receita_id}: {e}")
        return None

def update_producao(cursor, receita_id: int, observacao: str = None):
    # Esta função parece estar duplicada com 'iniciar_producao'.
    # Assumindo que a intenção é ATUALIZAR uma produção existente, a lógica seria:
    query = "UPDATE Producao SET status_producao = ?, observacao = ? WHERE receita_id = ? AND status_producao = 'Iniciada';"
    try:
        status_novo = 'Cancelada' # Exemplo
        cursor.execute(query, status_novo, observacao, receita_id)
        cursor.connection.commit()
        print(f"Produção da receita {receita_id} atualizada com sucesso.")
    except pyodbc.Error as e:
        cursor.connection.rollback()
        print(f"Erro ao atualizar produção para a receita {receita_id}: {e}")

def registrar_uma_pesagem(cursor, producao_id: int, etapa: str, peso: float, responsavel: str):
    sql_query = """
    INSERT INTO ProducaoPesagem (producao_id, etapa_processo, peso, data_pesagem, responsavel)
    VALUES (?, ?, ?, GETDATE(), ?);
    """
    try:
        cursor.execute(sql_query, producao_id, etapa, peso, responsavel)
        print(f"   -> Registro de pesagem para '{etapa}' com peso {peso} kg adicionado à transação.")
    except Exception as e:
        print(f"ERRO ao tentar executar o INSERT na tabela ProducaoPesagem: {e}")
        raise e

# --- LÓGICA DE CLP E PROCESSAMENTO ---

def processar_e_enviar_receita_para_clp(plc: LogixDriver, cursor, receita_id: int, reator_id: int) -> bool:
    detalhes_receita = get_receita_com_lotes_atribuidos(cursor, receita_id)
    if not detalhes_receita:
        print(f"Não foi encontrada nenhuma receita com ID {receita_id} ou ela não possui lotes atribuídos.")
        return False
    try:
        numero_produto = numero_produto_receita(cursor, receita_id)
        set_valor_receita_produto_id_to_clp(plc, reator_id, numero_produto)
        set_Recipe_Name_to_clp(plc, detalhes_receita['nome_receita'], reator_id)
        
        peso_total_Previsto = get_peso_total_previsto_por_id(cursor, receita_id)
        if peso_total_Previsto > 0:
            set_value_product_predicted_to_plc(plc, int(peso_total_Previsto), reator_id)

        total_lotes_na_receita = sum(len(p['lotes_atribuidos']) for p in detalhes_receita['produtos'].values())
        if total_lotes_na_receita == 0: total_lotes_na_receita = 1
        load_acumulado = 0

        for i_produto, (produto_id, produto) in enumerate(detalhes_receita['produtos'].items()):
            indice_clp = i_produto
            peso_previsto_do_produto = produto['quantidade_necessaria']
            set_quantidade_produto_to_clp(plc, reator_id, indice_clp, peso_previsto_do_produto)

            load_acumulado += len(produto['lotes_atribuidos'])
            percentual_carga = (load_acumulado / total_lotes_na_receita) * 100
            set_value_bar_loading_to_plc(plc, int(percentual_carga))

            pacote_de_lotes = produto['lotes_atribuidos'][:4]
            if not pacote_de_lotes:
                pesos = [0] * 4; textos = [""] * 4
            else:
                pesos = [lote['peso_lote'] for lote in pacote_de_lotes] + [0] * (4 - len(pacote_de_lotes))
                textos = [lote['observacao'] for lote in pacote_de_lotes] + [""] * (4 - len(pacote_de_lotes))
            
            set_lotes_peso_from_clp(plc, indice_clp, *pesos, reator_id)
            set_lotes_TEXTO_from_clp(plc, indice_clp, *textos, reator_id)

        print(f"\n[Reator {reator_id}] Envio da receita para o CLP concluído com sucesso.")
        return True
    except Exception as e:
        print(f"[Reator {reator_id}] Ocorreu um erro ao enviar dados para o CLP: {e}")
        return False

def registrar_dados_finais_da_producao(plc: LogixDriver, cursor, producao_id: int, receita_id: int, reator_id: int):
    print(f"[Reator {reator_id}] Iniciando o registro dos dados finais de pesagem...")
    try:
        detalhes_receita = get_receita_com_lotes_atribuidos(cursor, receita_id)
        if not detalhes_receita:
            raise Exception(f"Não foi possível encontrar a receita {receita_id} para salvar os dados.")

        for i_produto, (produto_id, produto) in enumerate(detalhes_receita['produtos'].items()):
            indice_clp = i_produto
            lotes_enviados = produto['lotes_atribuidos'][:4]
            if not lotes_enviados: continue

            tags_pesos_a_ler = [f'ERP_REATOR{reator_id}.OUT_INFOR_LOTE[{indice_clp}].PESO_{i+1}' for i in range(4)]
            resultados_pesos = plc.read(*tags_pesos_a_ler)
            pesos_medidos = [res.value if res else 0.0 for res in resultados_pesos]

            for i, lote in enumerate(lotes_enviados):
                peso_medido = pesos_medidos[i]
                if peso_medido is not None and peso_medido > 0:
                    etapa_descritiva = f"Pesagem de {produto['nome_produto']} - Lote Obs: {lote['observacao']}"
                    registrar_uma_pesagem(cursor, producao_id, etapa_descritiva, peso_medido, "Sistema de Automação")

        cursor.execute("UPDATE Producao SET status_producao = ?, data_fim = GETDATE() WHERE producao_id = ?;", "Finalizada", producao_id)
        cursor.connection.commit()
        print(f"\n[Reator {reator_id}] SUCESSO! Dados de pesagem salvos no banco.")
        return True
    except Exception as e:
        print(f"ERRO GERAL [Reator {reator_id}] AO SALVAR DADOS: {e}. A transação foi revertida (rollback).")
        cursor.connection.rollback()
        return False

# --- FUNÇÃO PRINCIPAL DO REATOR ---

def processar_reator(reator_id: int, stop_event: Event, lock_receitas: Lock, receitas_processando: set):
    """
    Loop principal GENÉRICO que monitora um reator específico, com lógica de
    bloqueio para evitar que a mesma receita seja processada simultaneamente.
    """
    PLC_IP = get_plc_ip()
    SLOT_DO_CLP = 0
    caminho_conexao = f'{PLC_IP}/1/{SLOT_DO_CLP}'
    plc = None
    
    print(f"✅ [Reator {reator_id}] Thread iniciada. Monitorando...")

    while not stop_event.is_set():
        try:
            # --- Bloco de Gerenciamento da Conexão com o CLP ---
            if plc is None or not plc.connected:
                print(f"[Reator {reator_id}] Conectando ao CLP via: {caminho_conexao}...")
                if plc: plc.close()
                plc = LogixDriver(caminho_conexao, init_program_tags=False)
                plc.open()
                print(f"[Reator {reator_id}] Conectado com sucesso ao CLP.")

            # --- Início da Lógica de Produção ---
            if validador_send_lote(plc, reator_id):
                receita_id = get_Receitaid_from_clp(plc, reator_id)
                
                if not receita_id or receita_id == 0:
                    time.sleep(2)
                    continue

                # --- LÓGICA DE BLOQUEIO DE RECEITA ---
                receita_ja_em_uso = False
                with lock_receitas:
                    if receita_id in receitas_processando:
                        receita_ja_em_uso = True
                    else:
                        receitas_processando.add(receita_id)
                        print(f"🔵 [Reator {reator_id}] Receita {receita_id} BLOQUEADA para processamento.")

                if receita_ja_em_uso:
                    print(f"🟡 [Reator {reator_id}] Receita {receita_id} já está em uso por outro reator. Ignorando.")
                    set_validador_send_lote_concluido(plc, reator_id, False)
                    time.sleep(5)
                    continue
                # --- FIM DA LÓGICA DE BLOQUEIO ---

                cursor = Conexao_SQLSERVER(DB_CONFIG)
                if not cursor:
                    print(f"🔴 [Reator {reator_id}] Falha ao conectar ao banco. Tentando novamente em 10s.")
                    # Libera o bloqueio da receita se não conseguir conectar ao banco
                    with lock_receitas:
                        if receita_id in receitas_processando:
                            receitas_processando.remove(receita_id)
                    time.sleep(10)
                    continue

                try:
                    print(f"[Reator {reator_id}] CLP solicitou processamento da receita ID: {receita_id}")
                    observacao = f"Produção iniciada pelo Reator {reator_id}"
                    producao_id_atual = iniciar_producao(cursor, receita_id, observacao)
                    
                    if not producao_id_atual:
                        raise Exception(f"Falha ao iniciar a produção para a receita {receita_id}")

                    open_pop_up_loading_to_plc(plc, reator_id, True)
                    set_visble_send_lote_to_clp(plc, reator_id, True)

                    if processar_e_enviar_receita_para_clp(plc, cursor, receita_id, reator_id):
                        validador_set_bit_enviado_to_plc(plc, reator_id, True)
                        time.sleep(1)
                        validador_set_bit_enviado_to_plc(plc, reator_id, False)
                        open_pop_up_loading_to_plc(plc, reator_id, False)
                        set_value_bar_loading_to_plc(plc, 0)
                        set_validador_send_lote_concluido(plc, reator_id, False)

                        print(f"[Reator {reator_id}] Aguardando finalização ou cancelamento da receita pelo CLP...")
                        
                        while not stop_event.is_set():
                            if get_finaliza_receita(plc, reator_id):
                                print(f"🟢 [Reator {reator_id}] >>> SINAL DE FINALIZAÇÃO RECEBIDO! <<<")
                                registrar_dados_finais_da_producao(plc, cursor, producao_id_atual, receita_id, reator_id)
                                set_finaliza_receita(plc, reator_id, False)
                                break
                            
                            if get_exclusao_receita_to_clp(plc, reator_id):
                                print(f"🟠 [Reator {reator_id}] >>> SINAL DE CANCELAMENTO RECEBIDO! <<<")
                                update_producao(cursor, receita_id, f"Produção no Reator {reator_id} cancelada pelo operador")
                                break
                            
                            time.sleep(1)
                    else:
                        raise Exception("Falha ao processar e enviar receita para o CLP")

                except Exception as e:
                    print(f"🔴 ERRO [Reator {reator_id}] durante o processamento da receita: {e}")
                    validador_falha_set_bit_enviado_to_plc(plc, reator_id, True)
                    time.sleep(5)
                    validador_falha_set_bit_enviado_to_plc(plc, reator_id, False)
                    set_validador_send_lote_concluido(plc, reator_id, False)

                finally:
                    if cursor:
                        cursor.close()
                    # Libera o bloqueio da receita, não importa o que aconteça
                    with lock_receitas:
                        if receita_id in receitas_processando:
                            receitas_processando.remove(receita_id)
                            print(f"🔵 [Reator {reator_id}] Receita {receita_id} LIBERADA.")
                    print(f"\n[Reator {reator_id}] Conexão com o banco fechada. Aguardando próxima solicitação...")
            
            time.sleep(1)

        except PycommError as e:
            print(f"🔴 ERRO DE COMUNICAÇÃO [Reator {reator_id}]: {e}. Reconectando em 10s...")
            if plc: plc.close()
            plc = None
            time.sleep(10)
        
        except Exception as e:
            print(f"🔴 ERRO INESPERADO [Reator {reator_id}]: {e}")
            time.sleep(10)
            
    print(f"🛑 [Reator {reator_id}] Thread finalizada.")
