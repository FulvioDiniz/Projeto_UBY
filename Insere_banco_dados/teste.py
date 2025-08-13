import pyodbc

# Use EXATAMENTE a mesma string de conexão da sua aplicação
CONN_STR = (
    r'DRIVER={ODBC Driver 17 for SQL Server};'
    r'SERVER=FULVIO\FULVIO;'
    r'DATABASE=Banco reformulado;'
    r'UID=sa;'
    r'PWD=123456;'
)

# Use um produto_id que você tem certeza que existe na sua tabela ProdutoGlobal.
TEST_PRODUTO_ID = 2 

print("Iniciando teste de inserção com a cláusula OUTPUT...")
conn = None
try:
    # 1. Conectar ao banco
    conn = pyodbc.connect(CONN_STR)
    cursor = conn.cursor()
    print("Conexão bem-sucedida.")

    # 2. Inserir um registro usando a cláusula OUTPUT
    print(f"Tentando inserir um lote para o produto_id: {TEST_PRODUTO_ID}...")
    
    # <<<<<<<<<< MUDANÇA PRINCIPAL AQUI >>>>>>>>>>
    sql_insert_com_output = """
        INSERT INTO Lote (produto_id, quantidade_lote, peso_lote, observacao_lote)
        OUTPUT inserted.lote_id
        VALUES (?, ?, ?, ?);
    """
    
    # 3. Executar e já pegar o valor de retorno
    lote_id = cursor.execute(sql_insert_com_output, TEST_PRODUTO_ID, 99.99, 99.99, 'TESTE COM OUTPUT').fetchval()
    
    # 4. Mostrar o resultado
    print("\n--- RESULTADO DO TESTE ---")
    print(f"O ID do lote retornado foi: {lote_id}")
    print(f"O tipo do valor retornado é: {type(lote_id)}")

    if lote_id is not None and lote_id > 0:
        print("\nVEREDITO: SUCESSO! O método OUTPUT funcionou perfeitamente.")
        # Se funcionou, vamos apagar o lote de teste para não sujar o banco
        cursor.execute("DELETE FROM Lote WHERE lote_id = ?", lote_id)
        print(f"Lote de teste com ID {lote_id} foi removido.")
    else:
        print("\nVEREDITO: FALHA! Mesmo com o método OUTPUT, não obtivemos um ID.")
        
    conn.commit()
    print("\nTransação confirmada.")

except Exception as e:
    print(f"\nERRO CRÍTICO DURANTE O TESTE: {e}")
    if conn:
        print("Desfazendo alterações...")
        conn.rollback()
finally:
    if conn:
        conn.close()
        print("Conexão fechada.")