from pycomm3 import LogixDriver

def set_value_product_predicted_to_plc(plc_ip, valor,reator):
    with LogixDriver(plc_ip) as plc:
        if reator < 10:
            reator = str('0' + str(reator))
        tag_name = f'Param_Reator_{reator}.Product_predicted'
        plc.write((tag_name, valor))
        print(f"Valor de produto previsto enviado para o CLP TOTAL: {valor}")

# Seu código de teste permanece o mesmo
if __name__ == "__main__":
    print("Iniciando monitoramento do Reator 1...")
    set_value_product_predicted_to_plc("192.168.1.120", int(300.0), 1)