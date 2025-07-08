from pycomm3 import LogixDriver, PycommError

# --- CONFIGURAÇÕES ---
# ❗ Altere para o IP correto do seu CLP
PLC_IP = '192.168.13.200' 

# A tag exata que você quer escrever



def set_valor_receita_produto_id_to_clp(plc_ip, reator,produto_id):
    with LogixDriver(plc_ip) as plc:
        if reator < 10:
            reator = str('0' + str(reator))
        tag_name = f'Param_Reator_{reator}.Product_batch'
        plc.write((tag_name, produto_id))
        print("Receita enviada para o CLP.")
        

# --- Bloco de Execução Principal ---
if __name__ == "__main__":
    # Defina aqui o valor do peso que você quer enviar
    valor_para_escrever = 20020111.00

    # Chama a função para realizar a operação
    sucesso = set_valor_receita_produto_id_to_clp(PLC_IP, 1, valor_para_escrever)

    print("-" * 30)
    if sucesso:
        print("Operação finalizada com sucesso.")
    else:
        print("A operação falhou. Verifique as mensagens de erro acima.")