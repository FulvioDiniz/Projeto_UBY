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

def get_receita_com_lotes_disponiveis(cursor, receita_id: int) -> dict | None:
    """
    Busca os detalhes de uma receita, incluindo todos os LOTES DISPONÍVEIS para cada
    produto da receita.
    """
    query = """
    SELECT 
        r.receita_id, r.nome_receita,
        rp.receita_produto_id,
        pg.produto_id, pg.numero_produto, pg.nome AS produto_nome,
        rp.quantidade_total AS quantidade_necessaria,
        l.lote_id, l.quantidade_lote, l.peso_lote, l.observacao_lote
    FROM [Receita] r
    JOIN [ReceitaProduto] rp ON r.receita_id = rp.receita_id
    JOIN [ProdutoGlobal] pg ON rp.produto_id = pg.produto_id
    LEFT JOIN [Lote] l ON pg.produto_id = l.produto_id
    WHERE r.receita_id = ?
    ORDER BY pg.numero_produto, l.lote_id;
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
            if row.numero_produto not in receita_info['produtos']:
                receita_info['produtos'][row.numero_produto] = {
                    'produto_id': row.produto_id,
                    'receita_produto_id': row.receita_produto_id,
                    'nome_produto': row.produto_nome,
                    'quantidade_necessaria': row.quantidade_necessaria,
                    'lotes_disponiveis': []
                }
            
            if row.lote_id:
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

# --- FUNÇÕES DE GERENCIAMENTO DA PRODUÇÃO (Suas novas funções) ---

def iniciar_producao(cursor, receita_id: int, observacao: str = None) -> int | None:
    """
    Cria um novo registro na tabela Producao para marcar o início de uma produção.
    """
    query = """
    INSERT INTO Producao (receita_id, data_inicio, status_producao, observacao)
    VALUES (?, ?, ?, ?);
    SELECT SCOPE_IDENTITY();
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

# --- LÓGICA PRINCIPAL DE INTERAÇÃO COM CLP (Seu código antigo, agora refatorado) ---

def processar_e_enviar_receita_para_clp(cursor, receita_id: int):
    """
    Busca os detalhes da receita no banco e envia para o CLP.
    """
    PLC_IP = get_plc_ip()
    detalhes_receita = get_receita_com_lotes_disponiveis(cursor, receita_id)
    
    if not detalhes_receita:
        print(f"Não foi encontrada nenhuma receita com ID {receita_id}.")
        return False

    try:
        # Envia nome da receita e quantidade de produtos
        set_Recipe_Name_to_clp(PLC_IP, detalhes_receita['nome_receita'], 1)
        total_de_produtos = len(detalhes_receita['produtos'])
        set_quantidade_produto_to_clp(PLC_IP, 0, total_de_produtos, 1)

        # Calcula o total de lotes para a barra de progresso
        total_lotes_na_receita = sum(len(p['lotes_disponiveis']) for p in detalhes_receita['produtos'].values())
        if total_lotes_na_receita == 0: total_lotes_na_receita = 1 # Evitar divisão por zero

        somador_peso_total = 0
        load_acumulado = 0

        # Itera sobre os produtos da receita
        for i, (num_produto, produto) in enumerate(detalhes_receita['produtos'].items()):
            print(f"\nProcessando Produto {num_produto} ({produto['nome_produto']})")
            
            # Envia o ID do produto para o CLP
            set_valor_receita_produto_id_to_clp(PLC_IP, i, num_produto) # Envia o ID real do produto
            
            somador_peso_total += produto['quantidade_necessaria']
            
            # Atualiza a barra de progresso
            load_acumulado += len(produto['lotes_disponiveis'])
            percentual_carga = (load_acumulado / total_lotes_na_receita) * 100
            set_value_bar_loading_to_plc(PLC_IP, int(percentual_carga))
            print(f"Progresso: {int(percentual_carga)}%")

            # Envia os lotes para o CLP
            lotes = produto['lotes_disponiveis']
            # Adapte esta parte se precisar enviar mais de 4 lotes
            pesos = [l['quantidade_lote'] for l in lotes] + [0] * (4 - len(lotes))
            textos = [l['observacao'] for l in lotes] + [""] * (4 - len(lotes))
            
            set_lotes_peso_from_clp(PLC_IP, i, *pesos, 1)
            set_lotes_TEXTO_from_clp(PLC_IP, i, *textos, 1)

        print(f"\nPeso total previsto: {somador_peso_total}")
        set_value_product_predicted_to_plc(PLC_IP, somador_peso_total, 1)
        return True

    except Exception as e:
        print(f"Ocorreu um erro ao enviar dados para o CLP: {e}")
        return False

def registrar_dados_finais_da_producao(cursor, producao_id: int, receita_id: int):
    """
    Busca os pesos medidos do CLP e os registra no banco de dados.
    """
    PLC_IP = get_plc_ip()
    print("Buscando dados finais de pesagem do CLP...")
    
    detalhes_receita = get_receita_com_lotes_disponiveis(cursor, receita_id)
    if not detalhes_receita:
        print(f"Erro: Não foi possível encontrar a receita {receita_id} para salvar os dados.")
        return False

    try:
        # Estrutura para mapear os pesos do CLP de volta aos produtos/lotes
        # ASSUMINDO que o CLP retorna um vetor plano de pesos na mesma ordem que foram enviados
        mapa_pesagem = []
        for num_produto, produto in detalhes_receita['produtos'].items():
            for lote in produto['lotes_disponiveis']:
                mapa_pesagem.append({
                    "receita_produto_id": produto['receita_produto_id'],
                    "lote_id": lote['lote_id'],
                    "nome_produto": produto['nome_produto']
                })

        # Busca o vetor de pesos do CLP
        # A lógica de `int(len(mapa_pesagem)/4.0)` precisa ser confirmada.
        # Se for um vetor simples, o segundo argumento pode ser o tamanho total.
        num_leituras = len(mapa_pesagem)
        vetor_pesos_medidos = get_vetor_de_envio_ERP(PLC_IP, 1, num_leituras) # Ajuste se necessário

        if len(vetor_pesos_medidos) != num_leituras:
            print(f"AVISO: O número de pesos recebidos do CLP ({len(vetor_pesos_medidos)}) não corresponde ao esperado ({num_leituras}).")

        # Inicia a transação
        for i, peso in enumerate(vetor_pesos_medidos):
            if i < len(mapa_pesagem):
                info = mapa_pesagem[i]
                registrar_pesagem(
                    cursor=cursor,
                    producao_id=producao_id,
                    etapa=f"Pesagem de {info['nome_produto']}",
                    peso=peso,
                    responsavel="Sistema de Automação",
                    receita_produto_id=info['receita_produto_id'],
                    lote_id=info['lote_id']
                )
        
        # Se tudo ocorreu bem, comita todas as alterações
        cursor.connection.commit()
        print("Todos os dados de pesagem foram salvos com sucesso no banco de dados.")
        return True

    except Exception as e:
        # Se qualquer erro ocorrer, reverte a transação inteira
        cursor.connection.rollback()
        print(f"ERRO GERAL AO SALVAR DADOS DA PRODUÇÃO: {e}. A transação foi revertida.")
        return False


def Reator1():
    """
    Loop principal que monitora o CLP para iniciar e finalizar produções.
    """
    while True:
        PLC_IP = get_plc_ip()
        if not PLC_IP:
            print("IP do CLP não configurado. Verifique as configurações.")
            time.sleep(10)
            continue

        if not validador_de_comunicacao_to_clp(PLC_IP):
            print("Erro de comunicação com o CLP. Tentando novamente...")
            time.sleep(5)
            continue

        # Verifica se o CLP solicitou o início do envio de uma receita
        if validador_send_lote(PLC_IP, 1):
            cursor = Conexao_SQLSERVER(DB_CONFIG)
            if not cursor:
                print("Falha ao conectar ao banco de dados. O processo não pode continuar.")
                time.sleep(10)
                continue

            try:
                receita_id = get_Receitaid_from_clp(PLC_IP, 1)
                print(f"CLP solicitou o processamento da receita ID: {receita_id}")

                # 1. Inicia um novo registro de produção no banco
                producao_id_atual = iniciar_producao(cursor, receita_id, "Produção iniciada pelo Reator 1")
                
                if producao_id_atual:
                    # Mostra pop-up de carregamento no CLP
                    open_pop_up_loading_to_plc(PLC_IP, 1)
                    set_visble_send_lote_to_clp(PLC_IP, 1, 1)

                    # 2. Processa e envia os dados da receita para o CLP
                    sucesso_envio = processar_e_enviar_receita_para_clp(cursor, receita_id)

                    if sucesso_envio:
                        # Sinaliza sucesso no CLP e aguarda finalização
                        validador_set_bit_enviado_to_plc(PLC_IP, 1)
                        time.sleep(5)
                        validador_set_bit_enviado_to_plc(PLC_IP, 0)
                        open_pop_up_loading_to_plc(PLC_IP, 0)
                        set_value_bar_loading_to_plc(PLC_IP, 0)
                        set_validador_send_lote_concluido(PLC_IP, 1, 0) # Limpa o bit de solicitação

                        print("Aguardando finalização da receita pelo CLP...")
                        # 3. Loop de espera pelo sinal de finalização do CLP
                        max_attempts = 300  # 5 minutos
                        for _ in range(max_attempts):
                            if get_finaliza_receita(PLC_IP, 1):
                                print("Sinal de finalização recebido!")
                                # 4. Registra os dados finais da produção
                                registrar_dados_finais_da_producao(cursor, producao_id_atual, receita_id)
                                set_finaliza_receita(PLC_IP, 1, 0) # Limpa o bit de finalização
                                break
                            
                            if get_exclusao_receita_to_clp(PLC_IP, 1):
                                print("Processo cancelado pelo operador no CLP.")
                                # Aqui você pode adicionar lógica para atualizar o status da produção para "Cancelada"
                                break
                            
                            time.sleep(1)
                        else:
                            print("Timeout: Processo da receita excedeu o tempo limite.")

                    else: # Falha no envio para o CLP
                        open_pop_up_loading_to_plc(PLC_IP, 0)
                        validador_falha_set_bit_enviado_to_plc(PLC_IP, 1)
                        time.sleep(5)
                        validador_falha_set_bit_enviado_to_plc(PLC_IP, 0)
                
                else: # Falha ao iniciar a produção no banco
                    print(f"Falha ao iniciar a produção para a receita {receita_id} no banco de dados.")
                    # Sinalizar erro no CLP
                    validador_falha_set_bit_enviado_to_plc(PLC_IP, 1)
                    time.sleep(5)
                    validador_falha_set_bit_enviado_to_plc(PLC_IP, 0)

            finally:
                # Garante que a conexão com o banco seja sempre fechada
                if cursor:
                    cursor.close()
                print("\nConexão com o banco fechada. Aguardando próxima solicitação...")
        
        time.sleep(1) # Pequena pausa para não sobrecarregar a CPU


if __name__ == "__main__":
    print("Iniciando monitoramento do Reator 1...")
    #Reator1()
    dados_receita = get_receita_com_lotes_disponiveis(Conexao_SQLSERVER(DB_CONFIG), 20250002)
    print(dados_receita['nome_receita'])  # Exibe o nome da receita
    #for i, (num_produto, produto) in enumerate(dados_receita['produtos'].items()):
            #print(f"\nProcessando Produto {num_produto} ({produto['nome_produto']})")
    