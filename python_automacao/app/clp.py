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
    
def set_produtos_lote_to_clp(plc_ip, contador,posicao_peso, valor):
    with LogixDriver(plc_ip) as plc:
        print(f"contador: {contador}")
        tag_name = f'REATOR_01_ERP.IN_INFOR_LOTE[{contador}].PESO_{posicao_peso}'
        plc.write((tag_name, valor))
        print(f"Produtos enviados para o CLP: {valor}")

def set_lotes_peso_from_clp(plc_ip,posicao, peso1, peso2, peso3, peso4):
    with LogixDriver(plc_ip) as plc:
        #tag_lote_peso1 = f'REATOR_01_ERP.IN_INFOR_LOTE[{posicao}].PESO_1'
        #tag_lote_peso2 = f'REATOR_01_ERP.IN_INFOR_LOTE[{posicao}].PESO_2'
        #tag_lote_peso3 = f'REATOR_01_ERP.IN_INFOR_LOTE[{posicao}].PESO_3'
        #tag_lote_peso4 = f'REATOR_01_ERP.IN_INFOR_LOTE[{posicao}].PESO_4'
        tag_lote_peso1 = f'ERP_REATOR1.IN_INFOR_LOTE[{posicao}].PESO_1'
        tag_lote_peso2 = f'ERP_REATOR1.IN_INFOR_LOTE[{posicao}].PESO_2'
        tag_lote_peso3 = f'ERP_REATOR1.IN_INFOR_LOTE[{posicao}].PESO_3'
        tag_lote_peso4 = f'ERP_REATOR1.IN_INFOR_LOTE[{posicao}].PESO_4'
        plc.write((tag_lote_peso1, peso1))
        plc.write((tag_lote_peso2, peso2))
        plc.write((tag_lote_peso3, peso3))
        plc.write((tag_lote_peso4, peso4))
        print(f"Lotes e pesos enviados para o CLP: {posicao}, {peso1}, {peso2}, {peso3}, {peso4}")

def set_produtos_to_clp(plc_ip, produtos):
    with LogixDriver(plc_ip) as plc:
        for index, produto in enumerate(produtos):
            tag_name = f'ERP_REATOR1.IN_INFOR_LOTE[{index}].PRODUTO'
            plc.write((tag_name, produto))
        print(f"Produtos enviados para o CLP: {produtos}")



def get_lotes_peso_from_clp(plc_ip):
    with LogixDriver(plc_ip) as plc:
        lotes = []
        for index in range(0, 10):
            tag_name = f'REATOR_01_ERP.IN_INFOR_LOTE[{index}].PESO_1'
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
        result = plc.read('Param_Reator_01.Receita_ID')
        if result:
            return result.value
        return None