from pycomm3 import LogixDriver

PLC_IP = '192.168.0.10'



def set_value_bar_loading_to_plc(plc_ip, valor):
    with LogixDriver(plc_ip) as plc:
        tag_name = 'CARREGANDO'
        plc.write((tag_name, valor))
        print(f"Valor de barra de carregamento enviado para o CLP: {valor}")

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
        set_value_bar_loading_to_plc(PLC_IP, 50)
    else:
        print("Falha na comunicação com o CLP.")

if __name__ == "__main__":
    main()

