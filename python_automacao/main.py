from app.recipes import get_recipe_from_db
from app.recipes_feitas import save_recipe_step_to_db, confirm_recipe_step_in_db
from app.clp import *
from config.settings import PLC_IP
from app.database import *
import time

def main():    
    # Quando a receita é iniciada, lê o valor de Name_Product
    '''while True:
        name_product = get_name_product_from_clp(PLC_IP)
        print(f"Receita identificada: {name_product}")
        print("Aperta 1 para enviar os pesos")
        if input() == '1':
            set_lotes_peso_from_clp(PLC_IP,0,100,200,300,400)
            set_lotes_peso_from_clp(PLC_IP,1,400,300,200,100)
            set_lotes_peso_from_clp(PLC_IP,2,100,200,300,400)
            set_lotes_peso_from_clp(PLC_IP,3,400,300,200,100)'''
    
# Criando alguns lotes para o primeiro produto
'''lote1 = Lote(1, "Lote A", 100)
lote2 = Lote(2, "Lote B", 150)
lote3 = Lote(3, "Lote C", 200)
lote4 = Lote(4, "Lote D", 250)

# Criando o primeiro produto com 4 lotes
produto1 = Produto(numero_produto=10, qtd_produto=700, 
                   lotes=[lote1, lote2, lote3, lote4], 
                   observacao="Produto X com 4 tanques/lotes")

# Criando lotes para um segundo produto (exemplo)
lote5 = Lote(5, "Lote E", 300)
lote6 = Lote(6, "Lote F", 350)

produto2 = Produto(numero_produto=20, qtd_produto=650, 
                   lotes=[lote5, lote6], 
                   observacao="Produto Y com 2 lotes")

# Criando a receita com os dois produtos
receita = Receita(produtos=[produto1, produto2])

print(receita)

               
               
       
    
if __name__ == "__main__":
    main()'''


def main():
    # Conecta ao banco
    cnxn = pyodbc.connect(DB_CONFIG)
    cursor = cnxn.cursor()
    # Define o ID da receita que deseja puxar
    receita_id = '020020111'
    receita_obj = get_receita_from_db(cursor, receita_id)
    
    if receita_obj is not None:
        print("Receita obtida do banco:")
        #set_Recipe_Name_to_clp(PLC_IP,  "BYOFOL") # Alterar nome da receita pegando direto do banco
        i = 0
        j = 0
        print(len(receita_obj.produtos))
        #get_produtos_name_to_clp(PLC_IP)
        #print(receita_obj)
        #print(receita_obj.produtos[0].lotes[0].qtd_produto_cada_lote)
        #set_lotes_peso_from_clp(PLC_IP, receita_obj.produtos, 100, 200, 300, 400)       
        for produto in receita_obj.produtos:
            #get_lotes_peso_from_clp(PLC_IP)
            #print(produto.observacao)
            #print(i)
            #set_Product_Name_Seq_to_clp(PLC_IP, produto.observacao,i)            
            #i = i + 1
            #valor_referencia = produto.numero_produto
            #print(f"Produto {produto.numero_produto} - Lote{i} : {lote.qtd_produto_cada_lote}")
            print("valor j ",j)
       
                #print(f"Produto {produto.numero_produto} - Lote {lote.numero_lote}: {lote.qtd_produto_cada_lote}")
            print(f"Produto {produto.numero_produto} ")
            print(len(receita_obj.produtos[j].lotes))
            match len(receita_obj.produtos[j].lotes):
                case 1:
                        set_lotes_peso_from_clp(PLC_IP, j, receita_obj.produtos[j].lotes[0].qtd_produto_cada_lote, 0, 0, 0)
                        #set_lotes_peso_from_clp(PLC_IP, produto.numero_produto, receita_obj.produtos[j].lotes[i].qtd_produto_cada_lote, 0, 0, 0)
                case 2:
                        set_lotes_peso_from_clp(PLC_IP, j, receita_obj.produtos[j].lotes[0].qtd_produto_cada_lote, receita_obj.produtos[j].lotes[1].qtd_produto_cada_lote, 0, 0)
                        #set_lotes_peso_from_clp(PLC_IP, produto.numero_produto, receita_obj.produtos[j].lotes[i].qtd_produto_cada_lote, receita_obj.produtos[j].lotes[i+1].qtd_produto_cada_lote, 0, 0)
                case 3:
                        set_lotes_peso_from_clp(PLC_IP, j, receita_obj.produtos[j].lotes[0].qtd_produto_cada_lote, receita_obj.produtos[j].lotes[1].qtd_produto_cada_lote, receita_obj.produtos[j].lotes[2].qtd_produto_cada_lote, 0)
                        #set_lotes_peso_from_clp(PLC_IP, produto.numero_produto, receita_obj.produtos[j].lotes[i].qtd_produto_cada_lote, receita_obj.produtos[j].lotes[i+1].qtd_produto_cada_lote, receita_obj.produtos[j].lotes[i+2].qtd_produto_cada_lote, 0)
                case 4:
                        set_lotes_peso_from_clp(PLC_IP, j, receita_obj.produtos[j].lotes[0].qtd_produto_cada_lote, receita_obj.produtos[j].lotes[1].qtd_produto_cada_lote, receita_obj.produtos[j].lotes[2].qtd_produto_cada_lote, receita_obj.produtos[j].lotes[3].qtd_produto_cada_lote)

                        #set_lotes_peso_from_clp(PLC_IP, produto.numero_produto, receita_obj.produtos[j].lotes[i].qtd_produto_cada_lote, receita_obj.produtos[j].lotes[i+1].qtd_produto_cada_lote, receita_obj.produtos[j].lotes[i+2].qtd_produto_cada_lote, receita_obj.produtos[j].lotes[i+3].qtd_produto_cada_lote)
                case _:
                        print("Nenhum lote encontrado")
              
                
               # if (len(receita_obj.produtos[j].lotes) < i):
                    #set_lotes_peso_from_clp(PLC_IP, produto.numero_produto, receita_obj.produtos[j].lotes[i].qtd_produto_cada_lote, 0, 0, 0)


                #set_lotes_peso_from_clp(PLC_IP, produto.numero_produto, receita_obj.produtos[j].lotes[i].qtd_produto_cada_lote, receita_obj.produtos[j].lotes[i+1].qtd_produto_cada_lote, receita_obj.produtos[j].lotes[i+2].qtd_produto_cada_lote, receita_obj.produtos[j].lotes[i+3].qtd_produto_cada_lote)
            j = j + 1

            
    
    # Fecha a conexão
    cursor.close()
    cnxn.close()


if __name__ == "__main__":
    main()
