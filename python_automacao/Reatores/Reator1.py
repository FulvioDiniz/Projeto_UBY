import pyodbc
from app.clp import *
#from config.settings import PLC_IP
from config.settings import get_plc_ip
from app.database import *
import time



PLC_IP = get_plc_ip()

def Validador_Encontra_receita(receita_id):
    cnxn = pyodbc.connect(DB_CONFIG)
    cursor = cnxn.cursor()
    receita = get_receita_from_db_novo(cursor, receita_id)
    if receita is not None:
        cursor.close()
        cnxn.close()
        return True
    else:
        cursor.close()
        cnxn.close()
        return False

def processar_receita_enviando_lote(receita_id):
    # Conecta ao banco
    cnxn = pyodbc.connect(DB_CONFIG)
    cursor = cnxn.cursor()
    
    # Busca a receita no banco (usa a função get_receita_from_db_novo adaptada à nova modelagem)
    receita_obj = get_receita_from_db_novo(cursor, receita_id)
    somador = 0
    load = 0
    val_total_load = 0
    divisor = Qnt_total_lotes_receitas_nova(cursor, receita_id)
    
    if receita_obj is not None:
        set_Recipe_Name_to_clp(get_plc_ip(), receita_obj.nome_receita, 1)
        # Removemos a referência a 'pord', pois na nova modelagem não é definida.
        # set_produto_id_to_clp(get_plc_ip(), 1, receita_obj.pord)
        
        # Percorre os produtos da receita
        for j, produto in enumerate(quantidade_produtos_receita_nova(cursor, receita_id_teste)):
            num_lotes = receita_obj.produtos[j].lotes
            print(f"\nProduto {produto.numero_produto} | Quantidade de lotes: {num_lotes}")
            # Usa o campo 'quantidade_total' (anteriormente 'qtd_produto') do produto
            set_quantidade_produto_to_clp(get_plc_ip(), j, quantidade_produtos_receita_nova(cursor, receita_id_teste), 1)
            somador += receita_obj.produtos[j].quantidade_total
            load = num_lotes / divisor
            val_total_load += load
            val_total_load_100 = val_total_load * 100
            set_value_bar_loading_to_plc(get_plc_ip(), int(val_total_load_100))
            print(f"Load: { int(val_total_load_100)}")
                        
            # Configura os lotes de acordo com a quantidade
            match num_lotes:
                case 1:
                    set_lotes_peso_from_clp(
                        get_plc_ip(),
                        j,
                        receita_obj.produtos[j].lotes[0].quantidade_lote,  # antes: qtd_produto_cada_lote
                        0, 0, 0, 1
                    )
                    set_lotes_TEXTO_from_clp(
                        get_plc_ip(),
                        j,
                        receita_obj.produtos[j].lotes[0].observacao_lote,  # antes: identificacao_lote
                        "", "", "", 1
                    )
                case 2:
                    set_lotes_peso_from_clp(
                        get_plc_ip(),
                        j,
                        receita_obj.produtos[j].lotes[0].quantidade_lote,
                        receita_obj.produtos[j].lotes[1].quantidade_lote,
                        0, 0, 1
                    )
                    set_lotes_TEXTO_from_clp(
                        get_plc_ip(),
                        j,
                        receita_obj.produtos[j].lotes[0].observacao_lote, receita_obj.produtos[j].lotes[1].observacao_lote,
                        "", "", 1
                    )
                case 3:
                    set_lotes_peso_from_clp(
                        get_plc_ip(),
                        j,
                        receita_obj.produtos[j].lotes[0].quantidade_lote,
                        receita_obj.produtos[j].lotes[1].quantidade_lote,
                        receita_obj.produtos[j].lotes[2].quantidade_lote,
                        0, 1
                    )
                    set_lotes_TEXTO_from_clp(
                        get_plc_ip(),
                        j,
                        receita_obj.produtos[j].lotes[0].observacao_lote, receita_obj.produtos[j].lotes[1].observacao_lote,
                        receita_obj.produtos[j].lotes[2].observacao_lote, "", 1
                    )
                case 4:
                    set_lotes_peso_from_clp(
                        get_plc_ip(),
                        j,
                        receita_obj.produtos[j].lotes[0].quantidade_lote,
                        receita_obj.produtos[j].lotes[1].quantidade_lote,
                        receita_obj.produtos[j].lotes[2].quantidade_lote,
                        receita_obj.produtos[j].lotes[3].quantidade_lote, 1
                    )
                    set_lotes_TEXTO_from_clp(
                        get_plc_ip(),
                        j,
                        receita_obj.produtos[j].lotes[0].observacao_lote, receita_obj.produtos[j].lotes[1].observacao_lote,
                        receita_obj.produtos[j].lotes[2].observacao_lote, receita_obj.produtos[j].lotes[3].observacao_lote, 1
                    )
                case _:
                    print("Nenhum lote encontrado para este produto.")
                    
        print(f"Somador: {somador}")
        set_value_product_predicted_to_plc(get_plc_ip(), somador, 1)
        cursor.close()
        cnxn.close()
        return True

 
        # Salva o passo da receita no banco          
    else:
        print(f"Não foi encontrada nenhuma receita com ID {receita_id}.")
        cursor.close()
        cnxn.close()
        return False
        
def carregar_pop_up_failed_to_plc(PLC_IP):
    print("Erro ao enviar lote para o CLP.")
    open_pop_up_loading_to_plc(PLC_IP,1)
    validador_falha_set_bit_enviado_to_plc(PLC_IP,1)
    time.sleep(5)
    open_pop_up_loading_to_plc(PLC_IP,0)
    validador_falha_set_bit_enviado_to_plc(PLC_IP,0)
    set_visble_send_lote_to_clp(PLC_IP,0,1)
    return False
    
def carregar_pop_up_sucess_to_plc(PLC_IP, receita_id):
    open_pop_up_loading_to_plc(PLC_IP,1)
    set_visble_send_lote_to_clp(PLC_IP,1,1)
    processar_receita_enviando_lote(receita_id)
    validador_set_bit_enviado_to_plc(PLC_IP,1)
    time.sleep(5)
    validador_set_bit_enviado_to_plc(PLC_IP,0)
    open_pop_up_loading_to_plc(PLC_IP,0)
    set_value_bar_loading_to_plc(PLC_IP, 0) 
    return True


def puxar_receita_do_clp(PLC_IP):
    receita_id = get_Receitaid_from_clp(PLC_IP,1)  
    print(receita_id)  
    if Validador_Encontra_receita(receita_id):
        referencia = carregar_pop_up_sucess_to_plc(PLC_IP, receita_id)
        set_validador_send_lote_concluido(PLC_IP,1,0)
        return referencia
        
    else:            
        return carregar_pop_up_failed_to_plc(PLC_IP)
    
def envia_receita_para_bd(PLC_IP):
    try:
        conn = pyodbc.connect(DB_CONFIG)
        cursor = conn.cursor()
        print("Conexão estabelecida com sucesso!")                                        
        receita_id = get_Receitaid_from_clp(PLC_IP,1)
        quantidade_lote = Qnt_total_lotes_receitas_nova(cursor, receita_id)                                                                            
        vetor_pesos_medidos = get_vetor_de_envio_ERP(PLC_IP, 1, int(quantidade_lote/4.0))                                     
        #envio_pesos_lote_salvo(cursor, receita_id, vetor_pesos_medidos)

    except Exception as e:
        print("Erro ao conectar ou inserir no SQL Server:", e)
        return False

    finally:
        try:
            cursor.close()
            conn.close()
            return True
        except:
            pass
    


def procuro_bit_finalizador_receita(PLC_IP):
    if get_finaliza_receita(PLC_IP,1):
        envia_receita_para_bd(PLC_IP)
        set_finaliza_receita(PLC_IP,1,0)
        
        return True
    else:
        return False

def Reator1():
    while True:
        PLC_IP = get_plc_ip()
        if validador_de_comunicacao_to_clp(PLC_IP):
            if validador_send_lote(PLC_IP,1):
                if puxar_receita_do_clp(PLC_IP):
                    while True:
                        if procuro_bit_finalizador_receita(PLC_IP) or get_exclusao_receita_to_clp(PLC_IP,1):
                            break
                        else:
                            print("Receita em processo...")
            else:
                print("Nenhuma receita encontrada.")
        else:
            print("Erro Conexão com clp na receita 1")
















                                                        
                                                        
                                                        
'''while True:        
        if get_plc_ip() == None:
            print("IP do CLP não configurado.")
        else:
            PLC_IP = get_plc_ip()            
            if validador_de_comunicacao_to_clp(PLC_IP):
                    print(validador_send_lote(PLC_IP,1))
                    receita_id = get_Receitaid_from_clp(PLC_IP,1)  
                    validador =  Validador_Encontra_receita(receita_id)     
                    print(f"Validador =  {validador}")   
                    print(get_plc_ip())  
                    print("Rodando...")
                    validador_coninuo_programa = validador_send_lote(PLC_IP,1)
                    print(flag)
                    if validador_coninuo_programa or flag == 1:                                
                            if validador == False and flag == 0:
                                carregar_pop_up_failed_to_plc(PLC_IP)
                            if validador == True:
                                print(f"Receita ID: {receita_id}")    
                                if flag != 1:             
                                    carregar_pop_up_sucess_to_plc(PLC_IP, receita_id)
                                    flag = 1                                    
                                while bit_receita_em_processo == 0:
                                    try:
                                        print("Receita em processo...")
                                        bit_receita_em_processo = get_finaliza_receita(PLC_IP,1)
                                    except:
                                        print("Erro ao ler bit de receita em processo.")
                                        break
                                try:
                                    conn = pyodbc.connect(DB_CONFIG)
                                    cursor = conn.cursor()
                                    print("Conexão estabelecida com sucesso!")
                                        
                                    receita_id = get_Receitaid_from_clp(PLC_IP,1)
                                    quantidade_lote = Qnt_total_lotes_receitas(cursor, receita_id)
                                    
                                        
                                    vetor_pesos_medidos = get_vetor_de_envio_ERP(PLC_IP, 1, int(quantidade_lote/4.0))
                                    print(len(vetor_pesos_medidos))

                                        # Chama a função para inserir em 'lote_salvo'
                                    envio_pesos_lote_salvo(cursor, receita_id, vetor_pesos_medidos)
                                    validador_coninuo_programa = set_validador_coninuo_programa_concluida(PLC_IP,1)
                                    receita_id = 0
                                    validador_coninuo_programa = set_validador_send_lote_concluido(PLC_IP,1,0)                                    
                                    flag = 0

                                except Exception as e:
                                    print("Erro ao conectar ou inserir no SQL Server:", e)

                                finally:
                                    try:
                                        cursor.close()
                                        conn.close()
                                    except:
                                        pass

                                            

            else:
                print("Erro ao enviar lote para o CLP 1.")
                set_visble_send_lote_to_clp(PLC_IP,0,1)
                print(get_plc_ip())'''

                                                                                                               
                                                        
                                                        
                                                        
                      #RECEITA FUNCIONANDO V.1                                  
                                                        
                                    
'''def Validador_Encontra_receita(receita_id):
    cnxn = pyodbc.connect(DB_CONFIG)
    cursor = cnxn.cursor()
    receita = get_receita_from_db(cursor, receita_id)
    if receita is not None:
        cursor.close()
        cnxn.close()
        return True
    else:
        cursor.close()
        cnxn.close()
        return False

def processar_receita_enviando_lote(receita_id):

    # Conecta ao banco
    cnxn = pyodbc.connect(DB_CONFIG)
    cursor = cnxn.cursor()
    
    # Busca a receita no banco
    receita_obj = get_receita_from_db(cursor, receita_id)
    somador = 0
    load = 0
    val_total_load = 0
    divisor = Qnt_total_lotes_receitas(cursor, receita_id)
    
    if receita_obj is not None:
        set_Recipe_Name_to_clp(get_plc_ip(), receita_obj.nome_receita,1)
        
        # Percorre os produtos da receita
        for j, produto in enumerate(receita_obj.produtos):
            num_lotes = len(produto.lotes)
            print(f"\nProduto: {produto.numero_produto} | Quantidade de lotes: {num_lotes}" )
            set_quantidade_produto_to_clp(get_plc_ip(), j, produto.qtd_produto,1)
            somador = produto.qtd_produto + somador
            load = len(produto.lotes)/divisor
            val_total_load = val_total_load + load
            val_total_load_100 = val_total_load*100
            set_value_bar_loading_to_plc(get_plc_ip(), int(val_total_load_100))
            print(f"Load: { int(val_total_load_100)}")
                        
            
            # Ajusta a configuração de lotes de acordo com a quantidade
            match num_lotes:
                case 1:
                    set_lotes_peso_from_clp(
                        get_plc_ip(),
                        j,
                        produto.lotes[0].qtd_produto_cada_lote,
                        0, 0, 0,1
                    )
                    set_lotes_TEXTO_from_clp(
                        get_plc_ip(),
                        j,
                        produto.lotes[0].identificacao_lote,"", "", "",1
                    )
                case 2:
                    set_lotes_peso_from_clp(
                        get_plc_ip(),
                        j,
                        produto.lotes[0].qtd_produto_cada_lote,
                        produto.lotes[1].qtd_produto_cada_lote,
                        0, 0,1
                    )
                    set_lotes_TEXTO_from_clp(
                        get_plc_ip(),
                        j,
                        produto.lotes[0].identificacao_lote, produto.lotes[1].identificacao_lote, "", "",1
                    )
                case 3:
                    set_lotes_peso_from_clp(
                        get_plc_ip(),
                        j,
                        produto.lotes[0].qtd_produto_cada_lote,
                        produto.lotes[1].qtd_produto_cada_lote,
                        produto.lotes[2].qtd_produto_cada_lote,
                        0,1
                    )
                    set_lotes_TEXTO_from_clp(
                        get_plc_ip(),
                        j,
                        produto.lotes[0].identificacao_lote, produto.lotes[1].identificacao_lote, produto.lotes[2].identificacao_lote, "",1
                    )
                case 4:
                    set_lotes_peso_from_clp(
                        get_plc_ip(),
                        j,
                        produto.lotes[0].qtd_produto_cada_lote,
                        produto.lotes[1].qtd_produto_cada_lote,
                        produto.lotes[2].qtd_produto_cada_lote,
                        produto.lotes[3].qtd_produto_cada_lote,1
                    )
                    set_lotes_TEXTO_from_clp(
                        get_plc_ip(),
                        j,
                        produto.lotes[0].identificacao_lote, produto.lotes[1].identificacao_lote, produto.lotes[2].identificacao_lote, produto.lotes[3].identificacao_lote,1
                    )
                    
                case _:
                    print("Nenhum lote encontrado para este produto.")
        print(f"Somador: {somador}")
        set_value_product_predicted_to_plc(get_plc_ip(), somador,1)
        cursor.close()
        cnxn.close()
        return True
 
        # Salva o passo da receita no banco          
    else:
        print(f"Não foi encontrada nenhuma receita com ID {receita_id}.")
        cursor.close()
        cnxn.close()
        return False
        
def carregar_pop_up_failed_to_plc(PLC_IP):
    print("Erro ao enviar lote para o CLP.")
    open_pop_up_loading_to_plc(PLC_IP,1)
    validador_falha_set_bit_enviado_to_plc(PLC_IP,1)
    time.sleep(5)
    open_pop_up_loading_to_plc(PLC_IP,0)
    validador_falha_set_bit_enviado_to_plc(PLC_IP,0)
    set_visble_send_lote_to_clp(PLC_IP,0,1)
    return False
    
def carregar_pop_up_sucess_to_plc(PLC_IP, receita_id):
    open_pop_up_loading_to_plc(PLC_IP,1)
    set_visble_send_lote_to_clp(PLC_IP,1,1)
    processar_receita_enviando_lote(receita_id)
    validador_set_bit_enviado_to_plc(PLC_IP,1)
    time.sleep(5)
    validador_set_bit_enviado_to_plc(PLC_IP,0)
    open_pop_up_loading_to_plc(PLC_IP,0)
    set_value_bar_loading_to_plc(PLC_IP, 0) 
    return True


def puxar_receita_do_clp(PLC_IP):
    receita_id = get_Receitaid_from_clp(PLC_IP,1)    
    if Validador_Encontra_receita(receita_id):
        referencia = carregar_pop_up_sucess_to_plc(PLC_IP, receita_id)
        set_validador_send_lote_concluido(PLC_IP,1,0)
        return referencia
        
    else:            
        return carregar_pop_up_failed_to_plc(PLC_IP)
    
def envia_receita_para_bd(PLC_IP):
    try:
        conn = pyodbc.connect(DB_CONFIG)
        cursor = conn.cursor()
        print("Conexão estabelecida com sucesso!")                                        
        receita_id = get_Receitaid_from_clp(PLC_IP,1)
        quantidade_lote = Qnt_total_lotes_receitas(cursor, receita_id)                                                                            
        vetor_pesos_medidos = get_vetor_de_envio_ERP(PLC_IP, 1, int(quantidade_lote/4.0))                                     
        envio_pesos_lote_salvo(cursor, receita_id, vetor_pesos_medidos)

    except Exception as e:
        print("Erro ao conectar ou inserir no SQL Server:", e)
        return False

    finally:
        try:
            cursor.close()
            conn.close()
            return True
        except:
            pass
    


def procuro_bit_finalizador_receita(PLC_IP):
    if get_finaliza_receita(PLC_IP,1):
        envia_receita_para_bd(PLC_IP)
        set_finaliza_receita(PLC_IP,1,0)
        
        return True
    else:
        return False

    
    



def Reator1():
    while True:
        PLC_IP = get_plc_ip()
        if validador_de_comunicacao_to_clp(PLC_IP):
            if validador_send_lote(PLC_IP,1):
                if puxar_receita_do_clp(PLC_IP):
                    while True:
                        if procuro_bit_finalizador_receita(PLC_IP) or get_exclusao_receita_to_clp(PLC_IP,1):
                            break
                        else:
                            print("Receita em processo...")
            else:
                print("Nenhuma receita encontrada.")
        else:
            print("Erro Conexão com clp na receita 1")



'''