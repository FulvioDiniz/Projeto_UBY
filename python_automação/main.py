from app.recipes import get_recipe_from_db
from app.recipes_feitas import save_recipe_step_to_db, confirm_recipe_step_in_db
from app.clp import get_name_product_from_clp, send_recipe_to_clp, get_confirma_product_from_clp, get_peso_product_from_clp, get_validador_incia_receita, get_sequencia_valor_produtos, get_sequencia_nome_produtos,set_lotes_peso_from_clp
from config.settings import PLC_IP
from Variaveis_Teste.Receita import Receita, Lote, Produto
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
    receita_id = 1
    receita_obj = get_receita_from_db(cursor, receita_id)
    
    if receita_obj is not None:
        print("Receita obtida do banco:")
        print(receita_obj)
        #print(receita_obj.produtos[0].lotes[0].qtd_produto_cada_lote)
    
    # Fecha a conexão
    cursor.close()
    cnxn.close()

if __name__ == "__main__":
    main()
