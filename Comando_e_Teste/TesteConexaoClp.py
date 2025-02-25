from pycomm3 import LogixDriver

PLC_IP = '192.168.0.10'



def validador_set_bit_enviado_to_plc(plc_ip,value):
    with LogixDriver(plc_ip) as plc:
        tag_name = plc.write('BIT_ENVIADO')
        plc.write((tag_name, 1))
        print(f"Bit de envio de lote ativado no CLP.")

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
        #validador_set_bit_enviado_to_plc(PLC_IP)
    else:
        print("Falha na comunicação com o CLP.")

if __name__ == "__main__":
    main()

