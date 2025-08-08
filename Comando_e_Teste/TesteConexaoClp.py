import time
from pycomm3 import LogixDriver, PycommError

# --- FUNÇÕES DE EXEMPLO (MOCKS) ---
# Substituímos todas as suas funções por valores fixos para isolar o problema.
# A única função real que usaremos é a de ler a tag de teste.

def get_plc_ip():
    """Retorna um IP fixo para o teste."""
    return '192.168.1.120'

def ler_tag_de_teste(plc: LogixDriver):
    """Uma função limpa para ler apenas a nossa tag de teste."""
    print("   -> Dentro do loop, tentando ler a tag 'TestePython'...")
    tag_lida = plc.read('TestePython')
    
    if tag_lida and tag_lida.value is not None:
        print(f"\n>>> SUCESSO DENTRO DO LOOP! A leitura da tag funcionou.")
        print(f"   Valor lido: {tag_lida.value}")
        return True
    else:
        print("\n!!! FALHA DENTRO DO LOOP! A leitura da tag falhou.")
        return False

# --- FUNÇÃO DE TESTE "ESTERILIZADA" ---
# Esta é a sua função Reator1, mas sem chamar nenhuma outra função sua.
def TesteReatorEsterilizado():
    PLC_IP = get_plc_ip()
    SLOT_DO_CLP = 0
    caminho_conexao = f'{PLC_IP}/1/{SLOT_DO_CLP}'
    plc = None

    print("--- Iniciando teste do Reator1 Esterilizado ---")
    print("Este teste executará o loop UMA VEZ para verificar a estabilidade da conexão.")

    try:
        # 1. Conectar (usando o método que falhava antes)
        if plc is None or not plc.connected:
            print(f"Conectando ao CLP via: {caminho_conexao}...")
            plc = LogixDriver(caminho_conexao, init_program_tags=False)
            plc.open()
            print(f"Conectado com sucesso ao CLP: {plc.info.get('product_name', 'N/A')}")

        # 2. Lógica Simulada (sem chamadas externas)
        print("\nSimulando que o CLP solicitou uma receita (if True)...")
        
        # 3. A única comunicação real com o CLP
        sucesso_leitura = ler_tag_de_teste(plc)

        if sucesso_leitura:
            print("\nDIAGNÓSTICO: A conexão e a leitura são estáveis dentro do loop.")
        else:
            print("\nDIAGNÓSTICO: A leitura falhou, mesmo com a conexão aberta.")

    except PycommError as e:
        print(f"\nERRO DE COMUNICAÇÃO: {e}")
    except Exception as e:
        print(f"\nERRO INESPERADO: {e}")
    finally:
        if plc and plc.connected:
            plc.close()
            print("\nConexão de teste fechada com sucesso.")

    print("\n--- Teste esterilizado finalizado. ---")


if __name__ == '__main__':
    TesteReatorEsterilizado()