from pycomm3 import LogixDriver, PycommError

'''REATOR 01 FUNÇÕES - VERSÃO CORRIGIDA'''

# A função 'validador_de_comunicacao_to_clp' não é mais necessária,
# pois o próprio loop principal em Reator1 já verifica 'plc.connected'.


def validador_de_comunicacao_to_clp(plc_ip: str) -> bool:
    """
    Realiza um teste de conexão rápido com o CLP.
    Ideal para ser usada por um front-end para verificar o status.
    Retorna True se a conexão for bem-sucedida, False caso contrário.
    """
    # Usamos o caminho e os parâmetros que descobrimos serem necessários
    caminho_conexao = f'{plc_ip}/1/0'
    
    print(f"Testando conexão com o CLP em {caminho_conexao}...")
    
    try:
        # O 'with' garante que a conexão será aberta e fechada automaticamente.
        with LogixDriver(caminho_conexao, init_program_tags=False) as plc:
            # Se a linha acima não gerou um erro, a conexão foi um sucesso.
            # O plc.info força a leitura de dados, validando a comunicação.
            if plc.info:
                print("Conexão com o CLP bem-sucedida.")
                return True
            else:
                # Caso raro onde a conexão abre mas não obtém informações
                print("Conexão com o CLP falhou ao obter informações.")
                return False

    except PycommError as e:
        print(f"Falha na comunicação com o CLP (pycomm3): {e}")
        return False
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao conectar ao CLP: {e}")
        return False


def set_Product_Name_Seq_to_clp(plc: LogixDriver, string: str, index: int, reator: int):
    tag_name = f'Product_Name_Seq_R{reator}[{index}]'
    plc.write(tag_name, string)
    print(f"Produto [{index}] enviado para o CLP: {string}")

def set_Recipe_Name_to_clp(plc: LogixDriver, string: str, reator: int):
    if reator < 10:
        reator = f'0{reator}'
    tag_name = f'Param_Reator_{reator}.Product_Name'
    plc.write(tag_name, string)
    print(f"Nome da receita enviada para o CLP: {string}")

def get_produtos_name_to_clp(plc: LogixDriver, reator: int):
    produtos = []
    # Cria uma lista de nomes de tags para uma leitura otimizada
    tags_a_ler = [f'Product_Name_Seq_R{reator}[{i}]' for i in range(10)]
    results = plc.read(*tags_a_ler) # Lê todas as 10 tags de uma vez
    if results:
        for r in results:
            produtos.append(r.value if r else None)
    print(f"Produtos obtidos do CLP: {produtos}")
    return produtos

def set_lotes_peso_from_clp(plc: LogixDriver, posicao: int, peso1, peso2, peso3, peso4, reator: int):
    # Escreve todas as 4 tags em uma única requisição para maior eficiência
    tags_a_escrever = [
        (f'ERP_REATOR{reator}.IN_INFOR_LOTE[{posicao}].PESO_1', peso1),
        (f'ERP_REATOR{reator}.IN_INFOR_LOTE[{posicao}].PESO_2', peso2),
        (f'ERP_REATOR{reator}.IN_INFOR_LOTE[{posicao}].PESO_3', peso3),
        (f'ERP_REATOR{reator}.IN_INFOR_LOTE[{posicao}].PESO_4', peso4)
    ]
    plc.write(*tags_a_escrever)
    print(f"Lotes e pesos enviados para o CLP: pos[{posicao}], {peso1}, {peso2}, {peso3}, {peso4}")

def set_lotes_TEXTO_from_clp(plc: LogixDriver, posicao: int, texto1, texto2, texto3, texto4, reator: int):
    # Escrita otimizada
    tags_a_escrever = [
        (f'ERP_REATOR{reator}.IN_INFOR_LOTE[{posicao}].TEXTO_1', texto1),
        (f'ERP_REATOR{reator}.IN_INFOR_LOTE[{posicao}].TEXTO_2', texto2),
        (f'ERP_REATOR{reator}.IN_INFOR_LOTE[{posicao}].TEXTO_3', texto3),
        (f'ERP_REATOR{reator}.IN_INFOR_LOTE[{posicao}].TEXTO_4', texto4)
    ]
    plc.write(*tags_a_escrever)
    print(f"Lotes e textos enviados para o CLP: pos[{posicao}], {texto1}, {texto2}, {texto3}, {texto4}")

def set_produtos_to_clp(plc: LogixDriver, produtos: list, reator: int):
    tags_a_escrever = []
    for index, produto in enumerate(produtos):
        tag_name = f'ERP_REATOR{reator}.IN_INFOR_LOTE[{index}].PRODUTO'
        tags_a_escrever.append((tag_name, produto))
    if tags_a_escrever:
        plc.write(*tags_a_escrever)
    print(f"Produtos enviados para o CLP: {produtos}")

def get_lotes_peso_from_clp(plc: LogixDriver, reator: int):
    lotes = []
    tags_a_ler = [f'REATOR_{reator}_ERP.IN_INFOR_LOTE[{i}].PESO_1' for i in range(10)]
    results = plc.read(*tags_a_ler)
    if results:
        for r in results:
            lotes.append(r.value if r else None)
    print(f"Lotes obtidos do CLP: {lotes}")
    return lotes

def get_validador_incia_receita(plc: LogixDriver, reator: int):
    if reator < 10:
        reator = f'0{reator}'
    tag_name = f'Param_Reator_{reator}.Sts_sent_OK'
    result = plc.read(tag_name)
    return result.value if result else None

def get_name_product_from_clp(plc: LogixDriver, reator: int): # BUG CORRIGIDO: adicionado 'reator'
    """Lê a variável Name_Product do CLP para identificar a receita."""
    if reator < 10:
        reator = f'0{reator}'
    tag_name = f'Param_Reator_{reator}.Product_Name'
    result = plc.read(tag_name)
    return result.value if result else None

def set_quantidade_produto_to_clp(plc: LogixDriver, reator: int, pos: int, quantidade):
    if reator < 10:
        reator = f'0{reator}'
    tag_name = f'Param_Reator_{reator}.Qtd_Additives[{pos}]'
    plc.write(tag_name, quantidade)
    print(f"CLP <- Tag: {tag_name} | Valor: {quantidade}")

def get_Receitaid_from_clp(plc: LogixDriver, reator: int):
    tag_name = f'Batch_Number_R{reator}'
    result = plc.read(tag_name)
    print(f"ID da Receita obtido do CLP: {result.value if result else 'Falha'}")
    return result.value if result else None

def validador_send_lote(plc: LogixDriver, reator: int):
    tag_name = f'Cmd_Search_Batch_R{reator}'
    result = plc.read(tag_name)
    print(f"Validador de envio de lote obtido do CLP{reator}: {result.value if result else 'Falha'}")
    return result.value if result else None

def set_validador_send_lote_concluido(plc: LogixDriver, reator: int, value):
    tag_name = f'Cmd_Search_Batch_R{reator}'
    plc.write(tag_name, value)
    print(f"Validador de envio de lote ({tag_name}) setado para: {value}")

def set_visble_send_lote_to_clp(plc: LogixDriver, reator: int, value): # Ordem dos parâmetros corrigida
    tag_name = f'Sts_Batch_OK_R{reator}'
    plc.write(tag_name, value)
    print(f"Visibilidade de envio de lote ({tag_name}) setada para: {value}")

def set_value_product_predicted_to_plc(plc: LogixDriver, valor, reator: int):
    if reator < 10:
        reator = f'0{reator}'
    tag_name = f'Param_Reator_{reator}.Product_predicted'
    plc.write(tag_name, valor)
    print(f"Valor de produto previsto enviado para o CLP TOTAL: {valor}")

def set_value_bar_loading_to_plc(plc: LogixDriver, valor):
    tag_name = 'CARREGANDO'
    plc.write(tag_name, valor)
    print(f"Valor de barra de carregamento enviado para o CLP: {valor}")

# VERSÃO CORRIGIDA (Substitua a antiga por esta)

def open_pop_up_loading_to_plc(plc: LogixDriver, reator: int, value: bool):
    """
    Controla o pop-up de carregamento para um reator específico.
    """
    # Usamos uma f-string para tornar o nome da tag dinâmico
    tag_name = f'BIT_LOADING_R{reator}' 
    
    try:
        plc.write(tag_name, value)
        print(f"Pop-up de carregamento para Reator {reator} setado para: {value}")
    except Exception as e:
        print(f"ERRO ao tentar escrever na tag '{tag_name}': {e}")
def validador_set_bit_enviado_to_plc(plc: LogixDriver, reator: int, value: bool):
    """
    Seta um bit de handshake para 'enviado com sucesso' para um reator específico.
    """
    # Usei um nome de tag dinâmico como exemplo. Adapte se o nome for diferente.
    tag_name = f'PC_Bit_Enviado_OK_R{reator}' 
    try:
        plc.write(tag_name, value)
        print(f"Bit de sucesso de envio para Reator {reator} ({tag_name}) setado para: {value}")
    except Exception as e:
        print(f"ERRO ao tentar escrever na tag '{tag_name}': {e}")


# APROVEITE E SUBSTITUA ESTA TAMBÉM

def validador_falha_set_bit_enviado_to_plc(plc: LogixDriver, reator: int, value: bool):
    """
    Seta um bit de handshake para 'falha no envio' para um reator específico.
    """
    # Usei um nome de tag dinâmico como exemplo. Adapte se o nome for diferente.
    tag_name = f'PC_Bit_Falha_Envio_R{reator}'
    try:
        plc.write(tag_name, value)
        print(f"Bit de falha de envio para Reator {reator} ({tag_name}) setado para: {value}")
    except Exception as e:
        print(f"ERRO ao tentar escrever na tag '{tag_name}': {e}")

def validador_falha_set_bit_enviado_to_plc(plc: LogixDriver, value):
    plc.write('BIT_NOT_ENVIADO', value)
    print(f"Bit de falha de envio de lote setado para: {value}")

def get_vetor_de_envio_ERP(plc: LogixDriver, reator: int, qtd_produto: int):
    vetor = []
    tags_a_ler = []
    for index in range(qtd_produto):
        tags_a_ler.append(f'ERP_REATOR{reator}.OUT_INFOR_LOTE[{index}].PESO_1')
        tags_a_ler.append(f'ERP_REATOR{reator}.OUT_INFOR_LOTE[{index}].PESO_2')
        tags_a_ler.append(f'ERP_REATOR{reator}.OUT_INFOR_LOTE[{index}].PESO_3')
        tags_a_ler.append(f'ERP_REATOR{reator}.OUT_INFOR_LOTE[{index}].PESO_4')
    
    results = plc.read(*tags_a_ler)
    if results:
        for r in results:
            vetor.append(r.value if r else None)
    print(f"Vetor de envio ERP obtido do CLP: {vetor}")
    return vetor

def get_finaliza_receita(plc: LogixDriver, reator: int):
    result = plc.read(f'ERP_REATOR{reator}.Bit_Volta')
    return result.value if result else None
    
def set_finaliza_receita(plc: LogixDriver, reator: int, value):
    plc.write(f'ERP_REATOR{reator}.Bit_Volta', value)
    print(f"Bit de finalização de receita ({f'ERP_REATOR{reator}.Bit_Volta'}) setado para: {value}")
    
def get_receita_em_processo_to_clp(plc: LogixDriver, reator: int):
    if reator < 10:
        reator = f'0{reator}'
    tag_name = f'Param_Reator_{reator}.Sts_sent_OK'
    result = plc.read(tag_name)
    print(f"Validador de receita em processo obtido do CLP: {result.value if result else 'Falha'}")
    return result.value if result else None

def get_exclusao_receita_to_clp(plc: LogixDriver, reator: int):
    """Lê o validador de exclusão de receita usando uma conexão existente."""
    tag_name = f'IHM_Aux_Product_R{reator}[0]'
    result = plc.read(tag_name)
    return result.value if result and result.value is not None else None

def set_valor_receita_produto_id_to_clp(plc: LogixDriver, reator: int, produto_id):
    if reator < 10:
        reator = f'0{reator}'
    tag_name = f'Param_Reator_{reator}.Product_batch'
    try:
        produto_id_int = int(produto_id)
        plc.write(tag_name, produto_id_int)
        print(f"ID do produto/lote ({produto_id_int}) enviado para {tag_name}.")
    except (ValueError, TypeError):
        print(f"ERRO: Não foi possível converter produto_id '{produto_id}' para inteiro.")