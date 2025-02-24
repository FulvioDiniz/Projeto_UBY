import pyodbc
from app.recipes_feitas import save_recipe_step_to_db, confirm_recipe_step_in_db
from app.clp import *
from config.settings import PLC_IP
from app.database import get_receita_from_db, DB_CONFIG


def processar_receita_enviando_lote(receita_id):

    # Conecta ao banco
    cnxn = pyodbc.connect(DB_CONFIG)
    cursor = cnxn.cursor()
    
    # Busca a receita no banco
    receita_obj = get_receita_from_db(cursor, receita_id)
    
    if receita_obj is not None:
        print(f"Receita {receita_id} obtida do banco com sucesso!")
        
        # Percorre os produtos da receita
        for j, produto in enumerate(receita_obj.produtos):
            num_lotes = len(produto.lotes)
            print(f"\nProduto: {produto.numero_produto} | Quantidade de lotes: {num_lotes}")
            
            # Ajusta a configuração de lotes de acordo com a quantidade
            match num_lotes:
                case 1:
                    set_lotes_peso_from_clp(
                        PLC_IP,
                        j,
                        produto.lotes[0].qtd_produto_cada_lote,
                        0, 0, 0
                    )
                case 2:
                    set_lotes_peso_from_clp(
                        PLC_IP,
                        j,
                        produto.lotes[0].qtd_produto_cada_lote,
                        produto.lotes[1].qtd_produto_cada_lote,
                        0, 0
                    )
                case 3:
                    set_lotes_peso_from_clp(
                        PLC_IP,
                        j,
                        produto.lotes[0].qtd_produto_cada_lote,
                        produto.lotes[1].qtd_produto_cada_lote,
                        produto.lotes[2].qtd_produto_cada_lote,
                        0
                    )
                case 4:
                    set_lotes_peso_from_clp(
                        PLC_IP,
                        j,
                        produto.lotes[0].qtd_produto_cada_lote,
                        produto.lotes[1].qtd_produto_cada_lote,
                        produto.lotes[2].qtd_produto_cada_lote,
                        produto.lotes[3].qtd_produto_cada_lote
                    )
                case _:
                    print("Nenhum lote encontrado para este produto.")
                    
    else:
        print(f"Não foi encontrada nenhuma receita com ID {receita_id}.")
    
    # Fecha a conexão com o banco
    cursor.close()
    cnxn.close()




def main():
    # Exemplo de uso da função
    #print(get_finalizador_receita(PLC_IP))
    if validador_de_comunicacao_to_clp(PLC_IP):
        receita_id = '020020111'
        processar_receita_enviando_lote(receita_id)


if __name__ == "__main__":
    main()
