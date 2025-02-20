from pycomm3 import LogixDriver

def get_name_product_from_clp(plc_ip):
    """Lê a variável Name_Product do CLP para identificar a receita."""
    with LogixDriver(plc_ip) as plc:
        result = plc.read('Param_Reator_01.Product_Name')
        if result:
            return result.value
        return None
    
def get_confirma_product_from_clp(plc_ip):
    with LogixDriver(plc_ip) as plc:
        result = plc.read('Param_Reator_05.Sts_Confirm')
        if result:
            return result.value
        return None

# Corrigido - uso de f-string para interpolar o índice
def get_sequencia_valor_produtos(plc_ip, index):
    with LogixDriver(plc_ip) as plc:
        # Use f-string para inserir o índice corretamente na tag
        result = plc.read(f'Param_Reator_05.Qtd_Additives[{index}]')
        if result:
            return result.value
        return None

# Corrigido - uso de f-string para interpolar o índice
def get_sequencia_nome_produtos(plc_ip, index):
    with LogixDriver(plc_ip) as plc:
        # Use f-string para inserir o índice corretamente na tag
        result = plc.read(f'Param_Reator_05.Product_Name_Seq[{index}]')
        if result:
            return result.value
        return None
    
def get_peso_product_from_clp(plc_ip):
    with LogixDriver(plc_ip) as plc:
        result = plc.read('Weight_Tare')
        if result:
            return result.value
        return None
    
def get_validador_incia_receita(plc_ip):
    with LogixDriver(plc_ip) as plc:
        result = plc.read('Param_Reator_05.Sts_sent_OK')
        if result:
            return result.value
        return None
    
def send_recipe_to_clp(recipe_name_seq, plc_ip):
    """Envia a sequência de produtos para o CLP."""
    with LogixDriver(plc_ip) as plc:
        for index, product in enumerate(recipe_name_seq):
            tag_name = f'Product_Name_Seq_R5[{index}]'
            plc.write((tag_name, product))
        print(f"Receita enviada para o CLP: {recipe_name_seq}")

def set_lotes_peso_from_clp(plc_ip,posicao, peso1, peso2, peso3, peso4):
    with LogixDriver(plc_ip) as plc:
        tag_lote_peso1 = f'ERP_REATOR1.IN_INFOR_LOTE[{posicao}].PESO_1'
        tag_lote_peso2 = f'ERP_REATOR1.IN_INFOR_LOTE[{posicao}].PESO_2'
        tag_lote_peso3 = f'ERP_REATOR1.IN_INFOR_LOTE[{posicao}].PESO_3'
        tag_lote_peso4 = f'ERP_REATOR1.IN_INFOR_LOTE[{posicao}].PESO_4'
        plc.write((tag_lote_peso1, peso1))
        plc.write((tag_lote_peso2, peso2))
        plc.write((tag_lote_peso3, peso3))
        plc.write((tag_lote_peso4, peso4))
        print(f"Lotes e pesos enviados para o CLP: {posicao}, {peso1}, {peso2}, {peso3}, {peso4}")