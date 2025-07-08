server = 'FULVIO\\FULVIO'        # Ex: 'localhost\\SQLEXPRESS'
database = 'UBY_ORIGIANAL'
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



#PLC_IP = '192.168.0.10'
