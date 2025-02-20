import pyodbc

# Configurações da conexão
server = 'FULVIO\\FULVIO'        # Ex: 'localhost\SQLEXPRESS'
database = 'TESTE'           # Ex: 'meuBanco'
username = 'sa'
password = '123456'

# Criação da string de conexão
connection_string = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password}'
)

# Estabelecendo a conexão
try:
    cnxn = pyodbc.connect(connection_string)
    cursor = cnxn.cursor()
    print("Conexão estabelecida com sucesso!")
    
    # Exemplo de consulta
    cursor.execute("SELECT @@version;")
    row = cursor.fetchone()
    while row:
        print(row[0])
        row = cursor.fetchone()

except Exception as e:
    print("Erro ao conectar ao SQL Server:", e)
