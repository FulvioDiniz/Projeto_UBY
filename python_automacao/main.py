import pyodbc
from app.recipes_feitas import save_recipe_step_to_db, confirm_recipe_step_in_db
from app.clp import *
from config.settings import PLC_IP
from app.database import get_receita_from_db, DB_CONFIG,Qnt_total_lotes_receitas
import time


def processar_receita_enviando_lote(receita_id):

    # Conecta ao banco
    cnxn = pyodbc.connect(DB_CONFIG)
    cursor = cnxn.cursor()
    
    # Busca a receita no banco
    receita_obj = get_receita_from_db(cursor, receita_id)
    somador = 0
    load = 0
    val_total_load = 0
    
    if receita_obj is not None:
        set_Recipe_Name_to_clp(PLC_IP, receita_obj.nome_receita)
        
        # Percorre os produtos da receita
        for j, produto in enumerate(receita_obj.produtos):
            num_lotes = len(produto.lotes)
            print(f"\nProduto: {produto.numero_produto} | Quantidade de lotes: {num_lotes}")
            set_quantidade_produto_to_clp(PLC_IP, j, produto.qtd_produto)
            somador = produto.qtd_produto + somador
            load = len(produto.lotes)/Qnt_total_lotes_receitas(cursor, receita_id)
            val_total_load = val_total_load + load
            val_total_load_100 = val_total_load*100
            set_value_bar_loading_to_plc(PLC_IP, int(val_total_load_100))
            print(f"Load: { int(val_total_load_100)}")
            time.sleep(2)            
            
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
        # Salva o passo da receita no banco          
    else:
        print(f"Não foi encontrada nenhuma receita com ID {receita_id}.")
    
    # Fecha a conexão com o banco
    cursor.close()
    cnxn.close()

 


def main():
    # Exemplo de uso da função
    #print(get_finalizador_receita(PLC_IP))
    while True:
        if validador_de_comunicacao_to_clp(PLC_IP):
            print(validador_send_lote(PLC_IP))
            if validador_send_lote(PLC_IP):
                receita_id = get_Receitaid_from_clp(PLC_IP)
                print(f"Receita ID: {receita_id}")
                open_pop_up_loading_to_plc(PLC_IP)
                processar_receita_enviando_lote(receita_id)
                set_visble_send_lote_to_clp(PLC_IP)
                print("Lote enviado com sucesso!")
                validador_set_bit_enviado_to_plc(PLC_IP,1)
                time.sleep(5)
                validador_set_bit_enviado_to_plc(PLC_IP,0)
                
            else:
                print("Erro ao enviar lote para o CLP.")
                #validador_falha_set_bit_enviado_to_plc(PLC_IP,1)
                #time.sleep(5)
                #validador_falha_set_bit_enviado_to_plc(PLC_IP,0)



if __name__ == "__main__":
    main()
