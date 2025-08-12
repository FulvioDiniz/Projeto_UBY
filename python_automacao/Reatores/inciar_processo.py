import threading
import time
from threading import Event

# Importa a função genérica que criamos no arquivo logica_reator.py
try:
    from .logica_reator import processar_reator
except ImportError:
    from logica_reator import processar_reator


# Define a quantidade de reatores que você quer monitorar
TOTAL_REATORES = 19

def iniciar_todos_os_reatores(stop_event: Event):
    """
    Esta função inicia e gerencia as threads para todos os reatores.
    """
    print(f"▶️ Orquestrador iniciado. Preparando para iniciar {TOTAL_REATORES} reatores...")

    threads_ativas = []
    
    # --- NOVO: Cria os recursos compartilhados aqui ---
    # O "cadeado" para garantir que apenas uma thread acesse o set por vez.
    lock_receitas = threading.Lock()
    # O "quadro de avisos" para registrar as receitas que já estão sendo processadas.
    receitas_em_processamento = set()
    
    # Cria e inicia uma thread para cada reator, de 1 a 19
    for i in range(1, TOTAL_REATORES + 1):
        reator_id = i
        
        # Cria a thread, passando a função alvo e os NOVOS argumentos
        thread = threading.Thread(
            target=processar_reator, 
            # Passa o reator_id, o sinal de parada, o cadeado e o quadro de avisos
            args=(reator_id, stop_event, lock_receitas, receitas_em_processamento), 
            daemon=True
        )
        thread.start()
        threads_ativas.append(thread)
        print(f"   -> Thread para o Reator {reator_id} iniciada.")
    
    print(f"\n✅ Todas as {len(threads_ativas)} threads dos reatores foram iniciadas. O sistema está operacional.")
    
    # Loop principal do orquestrador.
    while not stop_event.is_set():
        time.sleep(1)
    
    print("\n⏹️ Orquestrador recebendo sinal de parada. Todas as threads dos reatores serão finalizadas.")