# Configurações da conexão
server = 'FULVIO\\FULVIO'        # Ex: 'localhost\SQLEXPRESS'
database = 'TESTE'           # Ex: 'meuBanco'
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

def set_plc_ip(ip):
    global PLC_IP
    PLC_IP = ip

PLC_IP = '192.168.0.10'
