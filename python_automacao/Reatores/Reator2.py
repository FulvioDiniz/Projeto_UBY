import pyodbc
from app.recipes_feitas import save_recipe_step_to_db, confirm_recipe_step_in_db
from app.clp import *
from config.settings import PLC_IP
from app.database import get_receita_from_db, DB_CONFIG,Qnt_total_lotes_receitas
import time


def Validador_Encontra_receita(receita_id):
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
        set_Recipe_Name_to_clp(PLC_IP, receita_obj.nome_receita)
        
        # Percorre os produtos da receita
        for j, produto in enumerate(receita_obj.produtos):
            num_lotes = len(produto.lotes)
            print(f"\nProduto: {produto.numero_produto} | Quantidade de lotes: {num_lotes}")
            set_quantidade_produto_to_clp(PLC_IP, j, produto.qtd_produto)
            somador = produto.qtd_produto + somador
            load = len(produto.lotes)/divisor
            val_total_load = val_total_load + load
            val_total_load_100 = val_total_load*100
            set_value_bar_loading_to_plc(PLC_IP, int(val_total_load_100))
            print(f"Load: { int(val_total_load_100)}")
                        
            
            # Ajusta a configuração de lotes de acordo com a quantidade
            match num_lotes:
                case 1:
                    set_lotes_peso_from_clp(
                        PLC_IP,
                        j,
                        produto.lotes[0].qtd_produto_cada_lote,
                        0, 0, 0,1
                    )
                    set_lotes_TEXTO_from_clp(
                        PLC_IP,
                        j,
                        produto.lotes[0].identificacao_lote,"", "", ""
                    )
                case 2:
                    set_lotes_peso_from_clp(
                        PLC_IP,
                        j,
                        produto.lotes[0].qtd_produto_cada_lote,
                        produto.lotes[1].qtd_produto_cada_lote,
                        0, 0,1
                    )
                    set_lotes_TEXTO_from_clp(
                        PLC_IP,
                        j,
                        produto.lotes[0].identificacao_lote, produto.lotes[1].identificacao_lote, "", ""
                    )
                case 3:
                    set_lotes_peso_from_clp(
                        PLC_IP,
                        j,
                        produto.lotes[0].qtd_produto_cada_lote,
                        produto.lotes[1].qtd_produto_cada_lote,
                        produto.lotes[2].qtd_produto_cada_lote,
                        0,1
                    )
                    set_lotes_TEXTO_from_clp(
                        PLC_IP,
                        j,
                        produto.lotes[0].identificacao_lote, produto.lotes[1].identificacao_lote, produto.lotes[2].identificacao_lote, ""
                    )
                case 4:
                    set_lotes_peso_from_clp(
                        PLC_IP,
                        j,
                        produto.lotes[0].qtd_produto_cada_lote,
                        produto.lotes[1].qtd_produto_cada_lote,
                        produto.lotes[2].qtd_produto_cada_lote,
                        produto.lotes[3].qtd_produto_cada_lote,1
                    )
                    set_lotes_TEXTO_from_clp(
                        PLC_IP,
                        j,
                        produto.lotes[0].identificacao_lote, produto.lotes[1].identificacao_lote, produto.lotes[2].identificacao_lote, produto.lotes[3].identificacao_lote
                    )
                    
                case _:
                    print("Nenhum lote encontrado para este produto.")
        print(f"Somador: {somador}")
        set_value_product_predicted_to_plc(PLC_IP, somador)
        cursor.close()
        cnxn.close()
        return True
 
        # Salva o passo da receita no banco          
    else:
        print(f"Não foi encontrada nenhuma receita com ID {receita_id}.")
        cursor.close()
        cnxn.close()
        return False
        
    
    # Fecha a conexão com o banco


 


def Reator2():
    # Exemplo de uso da função
    #print(get_finalizador_receita(PLC_IP))
    bit_receita_em_processo = 0
    validador = False
    #bit_receita_finalizada = get_finaliza_receita(PLC_IP,1)
    flag = 0
    while True:
        if validador_de_comunicacao_to_clp(PLC_IP):
            print(validador_send_lote(PLC_IP))
            receita_id = get_Receitaid_from_clp(PLC_IP)  
            validador =  Validador_Encontra_receita(receita_id)     
            print(f"Validador =  {validador}")     
            print("Rodando...")
            validador_coninuo_programa = validador_send_lote(PLC_IP)
            print(flag)
            if validador_coninuo_programa or flag == 1:                                
                    if validador == False and flag == 0:
                        print("Erro ao enviar lote para o CLP 2 .")
                        open_pop_up_loading_to_plc(PLC_IP,1)
                        validador_falha_set_bit_enviado_to_plc(PLC_IP,1)
                        time.sleep(10)
                        open_pop_up_loading_to_plc(PLC_IP,0)
                        validador_falha_set_bit_enviado_to_plc(PLC_IP,0)
                        set_visble_send_lote_to_clp(PLC_IP,0)
                    if validador == True:
                        print(f"Receita ID: {receita_id}")    
                        if flag != 1:                
                            open_pop_up_loading_to_plc(PLC_IP,1)
                            set_visble_send_lote_to_clp(PLC_IP,1)
                            print("Lote enviado com sucesso!")
                            processar_receita_enviando_lote(receita_id)
                            validador_set_bit_enviado_to_plc(PLC_IP,1)
                            time.sleep(10)
                            validador_set_bit_enviado_to_plc(PLC_IP,0)
                            open_pop_up_loading_to_plc(PLC_IP,0)
                            set_value_bar_loading_to_plc(PLC_IP, 0) 
                            flag = 1                                    
                        while bit_receita_em_processo == 0:
                            try:
                                print("Receita em processo...")
                                bit_receita_em_processo = get_finaliza_receita(PLC_IP,1)
                            except:
                                print("Erro ao ler bit de receita em processo.")
                                break
                        try:
                            cnxn = pyodbc.connect(DB_CONFIG)
                            cursor = cnxn.cursor()
                            quantidade_de_lote = Qnt_total_lotes_receitas(cursor, receita_id)
                            get_vetor_de_envio_ERP(PLC_IP, 1, quantidade_de_lote)
                            cursor.close()
                            cnxn.close()
                            validador_coninuo_programa = 0
                            flag = 0
                        except:
                            print("Erro ao enviar vetor de envio para o ERP.")
                            
                        #break    
                                            
        else:
            print("Erro ao enviar lote para o CLP 2.")
                    #validador_falha_set_bit_enviado_to_plc(PLC_IP,1)
                    #time.sleep(5)
                    #validador_falha_set_bit_enviado_to_plc(PLC_IP,0)


