server = 'FULVIO\\FULVIO'        # Ex: 'localhost\\SQLEXPRESS'
database = 'Banco reformulado'
username = 'sa'
password = '123456'

# Criação da string de conexão
DB_CONFIG = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password}'
)

PLC_IP = None

def set_plc_ip(ip):
    global PLC_IP
    PLC_IP = ip
    
def get_plc_ip():
    return PLC_IP




import json
import os

# Define o nome do arquivo de configuração.
# Ele será criado na mesma pasta onde o script principal está sendo executado.
CONFIG_FILE = 'settings.json'

def set_plc_ip(ip_address: str):
    """
    Salva o endereço IP do CLP em um arquivo de configuração JSON.
    """
    try:
        data = {}
        # Tenta ler o arquivo existente para não apagar outras configurações
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
        
        # Atualiza o IP e escreve de volta no arquivo
        data['plc_ip'] = ip_address
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"IP '{ip_address}' salvo com sucesso em {CONFIG_FILE}")

    except (IOError, json.JSONDecodeError) as e:
        print(f"Erro ao salvar o arquivo de configuração: {e}")

def get_plc_ip() -> str:
    """
    Lê o endereço IP do CLP do arquivo de configuração JSON.
    Retorna uma string vazia se o arquivo ou a chave não existirem.
    """
    if not os.path.exists(CONFIG_FILE):
        return "" # Retorna vazio se o arquivo não existe

    try:
        with open(CONFIG_FILE, 'r') as f:
            data = json.load(f)
            # Usa .get() para retornar "" caso a chave 'plc_ip' não exista
            return data.get('plc_ip', "")
            
    except (IOError, json.JSONDecodeError) as e:
        print(f"Erro ao ler o arquivo de configuração: {e}")
        return "" # Retorna vazio em caso de erro