import os
import time
import psutil
import pyodbc
import threading
import tkinter as tk

from app.recipes_feitas import save_recipe_step_to_db, confirm_recipe_step_in_db
from app.clp import *
from config.settings import PLC_IP
from app.database import get_receita_from_db, DB_CONFIG, Qnt_total_lotes_receitas
from Reatores.Reator1 import Reator1

# Obtém o objeto do processo atual (para monitorar apenas este programa)
processo_atual = psutil.Process(os.getpid())

def update_stats(label, process):
    """
    Atualiza o texto do label com uso de CPU e memória do 'process'
    (apenas do processo Python atual).
    """
    # CPU em %, intervalo=0.1 para dar tempo de coleta (você pode ajustar)
    cpu_percent = process.cpu_percent(interval=0.1)
    # Memória RSS (Resident Set Size) em MB
    mem_info = process.memory_info().rss / (1024 ** 2)
    
    label.config(
        text=f" Gasto do Programa Reatores CPU: {cpu_percent:.1f}% | Memória: {mem_info:.1f} MB"
    )
    # Agenda a próxima atualização em 1 segundo (1000 ms)
    label.after(1000, update_stats, label, process)

def start_gui():
    """Inicia uma janela Tkinter para exibir o monitor de hardware do programa."""
    window = tk.Tk()
    window.title("Monitor de Hardware (Somente Meu Programa)")

    label = tk.Label(window, text="Iniciando monitoramento...", font=("Arial", 14))
    label.pack(padx=20, pady=20)

    # Faz a primeira chamada para atualizar o label
    update_stats(label, processo_atual)

    window.mainloop()

def main():
    """
    Cria uma thread para a janela de monitoramento,
    depois executa a função Reator1 normalmente.
    """
    # Inicia a GUI em uma thread separada, para não bloquear o resto do programa
    monitor_thread = threading.Thread(target=start_gui, daemon=True)
    monitor_thread.start()

    # Chama a lógica principal (no seu caso, Reator1)
    Reator1()

if __name__ == "__main__":
    main()
