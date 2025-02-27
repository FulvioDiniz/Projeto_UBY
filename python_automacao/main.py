import threading
import tkinter as tk
import psutil
import os
import time

# Importa os reatores (certifique-se de que os módulos estejam implementados)
from Reatores.Reator1 import Reator1
from Reatores.Reator2 import Reator2

# Obtém o objeto do processo atual para monitoramento
processo_atual = psutil.Process(os.getpid())


def main():

    
    # Lista com as funções dos reatores que serão executadas
    reatores = [Reator1, Reator2]
    
    threads = []
    
    # Cria e inicia uma thread para cada reator
    for reactor in reatores:
        t = threading.Thread(target=reactor, daemon=True)
        t.start()
        threads.append(t)
    
    # Opcional: aguarda as threads (se elas terminarem)
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
