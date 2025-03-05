from pycomm3 import LogixDriver

PLC_IP = '192.168.0.10'


        
def set_produto_id_to_clp(plc_ip, reator,produto_id):
    with LogixDriver(plc_ip) as plc:
        if reator < 10:
            reator = str('0' + str(reator))
        tag_name = f'Param_Reator_{reator}.Product_batch'
        plc.write((tag_name, produto_id))
        print("Receita enviada para o CLP.")
        
def test_connection_to_clp(plc_ip):
    """
    Tenta se conectar ao CLP. Se a conexão for estabelecida com sucesso,
    retorna True. Caso contrário, retorna False.
    """
    try:
        with LogixDriver(plc_ip) as plc:
            # Se entrar aqui, a conexão foi estabelecida com sucesso.
            return True
    except Exception as e:
        print(f"Erro ao conectar ao CLP: {e}")
        return False

def main():
    if test_connection_to_clp(PLC_IP):
        print("Conexão com o CLP estabelecida com sucesso!")
        set_produto_id_to_clp(PLC_IP, 1, 1234)
    else:
        print("Falha na comunicação com o CLP.")

if __name__ == "__main__":
    main()

