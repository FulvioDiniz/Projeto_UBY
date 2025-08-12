import threading
import tkinter as tk
import psutil
import os
import time

from Reatores.Reator1 import Reator1
from Reatores.Reator2 import Reator2

processo_atual = psutil.Process(os.getpid())


def main():

    
    # Lista com as funções dos reatores que serão executadas
    reatores = [Reator1,Reator2]
    
    threads = []
    
    for reactor in reatores:
        t = threading.Thread(target=reactor, daemon=True)
        t.start()
        threads.append(t)
    
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    print("Iniciando o script principal...")
    print(f"PID do processo atual: {processo_atual.pid}")
    main()
