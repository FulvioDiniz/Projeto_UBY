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

def update_stats(label, process):
    """
    Atualiza o label com o uso de CPU e memória do processo.
    """
    cpu_percent = process.cpu_percent(interval=0.1)
    mem_info = process.memory_info().rss / (1024 ** 2)
    label.config(text=f"CPU: {cpu_percent:.1f}% | Memória: {mem_info:.1f} MB")
    label.after(1000, update_stats, label, process)

def start_gui():
    """
    Inicia uma janela Tkinter para monitorar o uso de hardware.
    """
    window = tk.Tk()
    window.title("Monitor de Hardware")
    label = tk.Label(window, text="Iniciando monitoramento...", font=("Arial", 14))
    label.pack(padx=20, pady=20)
    update_stats(label, processo_atual)
    window.mainloop()

def main():
    """
    Inicia a GUI e os dois reatores em threads separadas.
    """
    # Inicia a GUI em uma thread separada para não bloquear o main
    gui_thread = threading.Thread(target=start_gui, daemon=True)
    gui_thread.start()
    
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
