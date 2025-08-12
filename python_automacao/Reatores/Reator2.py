import time

def Reator2():
    # Exemplo de uso da função
    #print(get_finalizador_receita(PLC_IP))
    while True:
        print("Reator 2")
        time.sleep(5)
    '''bit_receita_em_processo = 0
    validador = False
    #bit_receita_finalizada = get_finaliza_receita(PLC_IP,1)
    flag = 0
    if get_plc_ip() == None:
        print("IP do CLP não configurado.")
    else:
        PLC_IP = get_plc_ip()
        while True:
            if validador_de_comunicacao_to_clp(PLC_IP):
                print(validador_send_lote(PLC_IP))
                receita_id = get_Receitaid_from_clp(PLC_IP)  
                validador =  Validador_Encontra_receita(receita_id)     
                print(f"Validador =  {validador}")   
                print(get_plc_ip())  
                print("Rodando...")
                validador_coninuo_programa = validador_send_lote(PLC_IP)
                print(flag)
                if validador_coninuo_programa or flag == 1:                                
                        if validador == False and flag == 0:
                            print("Erro ao enviar lote para o CLP.")
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
                print("Erro ao enviar lote para o CLP 1.")
                print(get_plc_ip())
                        #validador_falha_set_bit_enviado_to_plc(PLC_IP,1)
                        #time.sleep(5)
                        #validador_falha_set_bit_enviado_to_plc(PLC_IP,0)'''


