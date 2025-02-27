from pycomm3 import LogixDriver
'''REATOR 01 FUNÇÕES'''


def validador_de_comunicacao_to_clp(plc_ip):
    try:
        with LogixDriver(plc_ip) as plc:
            return True
    except Exception as e:
        print(f"Erro ao conectar ao CLP: {e}")
        return False

def set_Product_Name_Seq_to_clp(plc_ip, string,index):
    with LogixDriver(plc_ip) as plc:
        tag_name = f'Product_Name_Seq_R1[{index}]'
        plc.write((tag_name, string))
        print(f"Produtos enviados para o CLP: {string}")

def set_Recipe_Name_to_clp(plc_ip, string):
    with LogixDriver(plc_ip) as plc:
        tag_name = f'Param_Reator_01.Product_Name'
        plc.write((tag_name, string))
        print(f"Nome da receita enviada para o CLP: {string}")
        

def get_produtos_name_to_clp(plc_ip):
    with LogixDriver(plc_ip) as plc:
        produtos = []
        for index in range(0, 10):
            tag_name = f'Product_Name_Seq_R1[{index}]'
            result = plc.read(tag_name)
            if result:
                produtos.append(result.value)
        print(f"Produtos obtidos do CLP: {produtos}")
        return produtos


def set_lotes_peso_from_clp(plc_ip,posicao, peso1, peso2, peso3, peso4,reator):
    with LogixDriver(plc_ip) as plc:
        tag_lote_peso1 = f'ERP_REATOR{reator}.IN_INFOR_LOTE[{posicao}].PESO_1'
        tag_lote_peso2 = f'ERP_REATOR{reator}.IN_INFOR_LOTE[{posicao}].PESO_2'
        tag_lote_peso3 = f'ERP_REATOR{reator}.IN_INFOR_LOTE[{posicao}].PESO_3'
        tag_lote_peso4 = f'ERP_REATOR{reator}.IN_INFOR_LOTE[{posicao}].PESO_4'
        plc.write((tag_lote_peso1, peso1))
        plc.write((tag_lote_peso2, peso2))
        plc.write((tag_lote_peso3, peso3))
        plc.write((tag_lote_peso4, peso4))
        print(f"Lotes e pesos enviados para o CLP: {posicao}, {peso1}, {peso2}, {peso3}, {peso4}")



def set_lotes_TEXTO_from_clp(plc_ip,posicao, TEXTO1, TEXTO2, TEXTO3, TEXTO4):
    with LogixDriver(plc_ip) as plc:
        tag_lote_peso1 = f'ERP_REATOR1.IN_INFOR_LOTE[{posicao}].TEXTO_1'
        tag_lote_peso2 = f'ERP_REATOR1.IN_INFOR_LOTE[{posicao}].TEXTO_2'
        tag_lote_peso3 = f'ERP_REATOR1.IN_INFOR_LOTE[{posicao}].TEXTO_3'
        tag_lote_peso4 = f'ERP_REATOR1.IN_INFOR_LOTE[{posicao}].TEXTO_4'
        plc.write((tag_lote_peso1, TEXTO1))
        plc.write((tag_lote_peso2, TEXTO2))
        plc.write((tag_lote_peso3, TEXTO3))
        plc.write((tag_lote_peso4, TEXTO4))
        print(f"Lotes e pesos enviados para o CLP: {posicao}, {TEXTO1}, {TEXTO2}, {TEXTO3}, {TEXTO4}")

def set_produtos_to_clp(plc_ip, produtos):
    with LogixDriver(plc_ip) as plc:
        for index, produto in enumerate(produtos):
            tag_name = f'ERP_REATOR1.IN_INFOR_LOTE[{index}].PRODUTO'
            plc.write((tag_name, produto))
        print(f"Produtos enviados para o CLP: {produtos}")



def get_lotes_peso_from_clp(plc_ip,reator):
    with LogixDriver(plc_ip) as plc:
        lotes = []
        for index in range(0, 10):
            tag_name = f'REATOR_{reator}_ERP.IN_INFOR_LOTE[{index}].PESO_1'
            result = plc.read(tag_name)
            if result:
                lotes.append(result.value)
        print(f"Lotes obtidos do CLP: {lotes}")
        return lotes

    
def get_validador_incia_receita(plc_ip):
    with LogixDriver(plc_ip) as plc:
        result = plc.read('Param_Reator_01.Sts_sent_OK')
        if result:
            return result.value
        return None
    
def get_name_product_from_clp(plc_ip):
    """Lê a variável Name_Product do CLP para identificar a receita."""
    with LogixDriver(plc_ip) as plc:
        result = plc.read('Param_Reator_01.Product_Name')
        if result:
            return result.value
        return None
    
def get_finalizador_receita(plc_ip):
    with LogixDriver(plc_ip) as plc:
        Contador = plc.read('Program:Reator_01.Cont_R1')
        if Contador:
            return Contador.value
        return None
    
def set_quantidade_produto_to_clp(plc_ip,pos, quantidade):
    with LogixDriver(plc_ip) as plc:
        tag_name = f'Param_Reator_01.Qtd_Additives[{pos}]'
        plc.write((tag_name, quantidade))
        print(f"Quantidade de produtos enviada para o CLP: {quantidade}")

def get_Receitaid_from_clp(plc_ip):
    with LogixDriver(plc_ip) as plc:
        result = plc.read('Param_Reator_01.Product_batch')
        if result:
            return result.value
        return None
    
def validador_send_lote(plc_ip):
    with LogixDriver(plc_ip) as plc:
        result = plc.read('Cmd_Search_Batch')
        if result:
            return result.value
        return None
    
def set_visble_send_lote_to_clp(plc_ip,value):
    with LogixDriver(plc_ip) as plc:
        plc.write("Sts_Batch_OK", value)
        print(f"Visibilidade de envio de lote enviada para o CLP: 1")

def set_value_product_predicted_to_plc(plc_ip, valor):
    with LogixDriver(plc_ip) as plc:
        tag_name = 'Param_Reator_01.Product_predicted'
        plc.write((tag_name, valor))
        print(f"Valor de produto previsto enviado para o CLP: {valor}")


def set_value_bar_loading_to_plc(plc_ip, valor):
    with LogixDriver(plc_ip) as plc:
        tag_name = 'CARREGANDO'
        plc.write((tag_name, valor))
        print(f"Valor de barra de carregamento enviado para o CLP: {valor}")

def open_pop_up_loading_to_plc(plc_ip,value):
    with LogixDriver(plc_ip) as plc:
        tag_name = 'BIT_LOADING'
        plc.write((tag_name, value))
        print(f"Pop-up de carregamento aberto no CLP.")


def validador_set_bit_enviado_to_plc(plc_ip,value):
    with LogixDriver(plc_ip) as plc:
        # Escreve diretamente no tag "BIT_ENVIADO" o valor 1
        plc.write("BIT_ENVIADO", value)
        print("Bit de envio de lote ativado no CLP.")


def validador_falha_set_bit_enviado_to_plc(plc_ip, value):
    with LogixDriver(plc_ip) as plc:
        plc.write('BIT_NOT_ENVIADO', value)
        print(f"Bit de envio de lote ativado no CLP.")

'''def get_vetor_de_envio_ERP(plc_ip):
    with LogixDriver(plc_ip) as plc:
        vetor = []
        for index in range(0, 10):
            tag_name = f'ERP_REATOR1.OUT_INFOR_LOTE[{index}]'
            result = plc.read(tag_name)
            if result:
                vetor.append(result.value)
        print(f"Vetor de envio ERP obtido do CLP: {vetor}")
        return vetor'''


# tag = REATOR_01.ERP.OUT_INFOR_LOTE[{index}].PESO_1

def get_vetor_de_envio_ERP(plc_ip, reator, qtd_lotes):
    with LogixDriver(plc_ip) as plc:
        vetor = []
        '''if reator < 10:
            reator = str('0' + str(reator))'''
        for index in range(0, qtd_lotes):
            
            tag_name = f'ERP_REATOR{reator}.OUT_INFOR_LOTE[{index}].PESO_1'
            tag_name2 = f'ERP_REATOR{reator}.OUT_INFOR_LOTE[{index}].PESO_2'
            tag_name3 = f'ERP_REATOR{reator}.OUT_INFOR_LOTE[{index}].PESO_3'
            tag_name4 = f'ERP_REATOR{reator}.OUT_INFOR_LOTE[{index}].PESO_4'
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



def get_finaliza_receita(plc_ip,reator):
    with LogixDriver(plc_ip) as plc:
        result = plc.read(f'ERP_REATOR{reator}.Bit_Volta')
        if result:
            return result.value
        return None
    
def set_finaliza_receita(plc_ip, reator):
    with LogixDriver(plc_ip) as plc:
        plc.write(f'ERP_REATOR{reator}.Bit_Volta', 1)
        print("Bit de finalização de receita ativado no CLP.")