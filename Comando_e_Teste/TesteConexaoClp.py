from pycomm3 import LogixDriver

PLC_IP = '192.168.0.11'


def get_vetor_de_envio_ERP(plc_ip, reator, qtd_lotes):
    with LogixDriver(plc_ip) as plc:
        vetor = []
        if reator < 10:
            reator = str('0' + str(reator))
            print(reator)
        for index in range(0, qtd_lotes):
            tag_name = f'REATOR_{reator}_ERP.OUT_INFOR_LOTE[{index}].PESO_1'
            tag_name2 = f'REATOR_{reator}_ERP.OUT_INFOR_LOTE[{index}].PESO_2'
            tag_name3 = f'REATOR_{reator}_ERP.OUT_INFOR_LOTE[{index}].PESO_3'
            tag_name4 = f'REATOR_{reator}_ERP.OUT_INFOR_LOTE[{index}].PESO_4'
            result = plc.read(tag_name)
            result2 = plc.read(tag_name2)
            result3 = plc.read(tag_name3)
            result4 = plc.read(tag_name4)
            if result:
                vetor.append(result.value)
                vetor.append(result2.value)
                vetor.append(result3.value)
                vetor.append(result4.value)
        print(f"Vetor de envio ERP obtido do CLP: {vetor}")

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
        get_vetor_de_envio_ERP(PLC_IP, 1, 3)
    else:
        print("Falha na comunicação com o CLP.")

if __name__ == "__main__":
    main()

