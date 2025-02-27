import os
import sys
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading
import psutil

# Ajusta sys.path para incluir o diretório python_automacao
current_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


from app.clp import validador_de_comunicacao_to_clp
from config.settings import set_plc_ip, get_plc_ip
from main import main as reatores_main

def resource_path(relative_path):
    """Retorna o caminho absoluto do recurso relativo a este script."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# Monitor de desempenho com psutil
processo_atual = psutil.Process(os.getpid())
def update_stats(label, process):
    cpu_percent = process.cpu_percent(interval=0.1)
    mem_info = process.memory_info().rss / (1024 ** 2)
    label.config(text=f"CPU: {cpu_percent:.1f}% | Memória: {mem_info:.1f} MB")
    label.after(1000, update_stats, label, process)

class CLPApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Conexão CLP")
        # Define a cor de fundo (usada como moldura, se necessário)
        self.configure(bg="#FFA500")
        # Não permite redimensionamento
        self.resizable(False, False)
        self.conectado = False
        self.clp_ip = get_plc_ip() or ''

        self._configurar_estilos()
        self._criar_widgets()
        
        # Ajusta o tamanho da janela para o tamanho requerido pelo container
        self.update_idletasks()
        width = self.container.winfo_reqwidth()
        height = self.container.winfo_reqheight()
        self.geometry(f"{width}x{height}")
        # Centraliza a janela na tela
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")

    def _configurar_estilos(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton",
                             font=("Segoe UI", 12, "bold"),
                             padding=10,
                             background="#FFA500",
                             foreground="white")
        self.style.map("TButton", background=[("active", "#e69500")])
        self.style.configure("Title.TLabel",
                             font=("Segoe UI", 24, "bold"),
                             foreground="#FFA500",
                             background="white")
        self.style.configure("Info.TLabel",
                             font=("Segoe UI", 14),
                             background="white",
                             foreground="#333333")

    def _criar_widgets(self):
        # Container principal que agrupa o card e o monitor
        self.container = tk.Frame(self, bg="white")
        self.container.pack(expand=True, fill="both")
        
        # Card com borda (fundo branco com leve relief)
        self.card = tk.Frame(self.container, bg="white", bd=0, relief="ridge")
        self.card.pack(padx=20, pady=20)
        
        # Logo pequena no card
        try:
            logo_path = resource_path(os.path.join("img", "Logo.jpg"))
            logo_image = Image.open(logo_path)
            max_width = 200
            ratio = max_width / logo_image.width
            new_width = int(logo_image.width * ratio)
            new_height = int(logo_image.height * ratio)
            logo_image = logo_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = tk.Label(self.card, image=self.logo_photo, bg="white")
            logo_label.pack(pady=(20, 10))
        except Exception as e:
            print("Erro ao carregar logo:", e)
            logo_label = tk.Label(self.card, text="Logo da Empresa", font=("Segoe UI", 18, "bold"), bg="white")
            logo_label.pack(pady=(20, 10))
        
        # Título
        self.title_label = ttk.Label(self.card, text="Conexão CLP", style="Title.TLabel")
        self.title_label.pack(pady=(0, 20))
        
        # Frame para configuração do IP
        ip_frame = tk.Frame(self.card, bg="white")
        ip_frame.pack(pady=10, padx=20)
        ip_label = ttk.Label(ip_frame, text="IP do CLP:", style="Info.TLabel")
        ip_label.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")
        self.ip_entry = ttk.Entry(ip_frame, font=("Segoe UI", 14))
        self.ip_entry.insert(0, self.clp_ip)
        self.ip_entry.grid(row=0, column=1, padx=(0, 10), pady=5)
        # Guarda referência do botão para bloqueio
        self.update_ip_btn = ttk.Button(ip_frame, text="Atualizar IP", command=self._atualizar_ip)
        self.update_ip_btn.grid(row=0, column=2, padx=(0, 10), pady=5)
        
        # Status e botão de conexão
        self.status_label = tk.Label(self.card,
                                     text="Desconectado",
                                     font=("Segoe UI", 14, "bold"),
                                     bg="#dc3545",
                                     fg="white",
                                     width=15,
                                     height=2)
        self.status_label.pack(pady=10)
        self.toggle_button = ttk.Button(self.card, text="Conectar", command=self._toggle_conexao)
        self.toggle_button.pack(pady=(10, 20))
        
        # Monitor de desempenho (centralizado abaixo do card)
        self.monitor_label = tk.Label(self.container, text="", font=("Arial", 12), bg="#FFA500", fg="white")
        self.monitor_label.pack(pady=(0, 20))
        update_stats(self.monitor_label, processo_atual)
    
    def _atualizar_ip(self):
        # Bloqueia o botão para evitar cliques repetidos
        self.update_ip_btn.config(state="disabled")
        novo_ip = self.ip_entry.get().strip()
        if not novo_ip:
            print("IP inválido: campo vazio")
            self.status_label.config(text="IP inválido", bg="#dc3545")
            self.after(2000, lambda: self.update_ip_btn.config(state="normal"))
            return
        
        # Verifica a comunicação com o CLP
        if not validador_de_comunicacao_to_clp(novo_ip):
            print("Falha na comunicação com o CLP")
            self.status_label.config(text="Erro comunicação", bg="#dc3545")
            self.after(2000, lambda: self.update_ip_btn.config(state="normal"))
            return

        # Se passou na validação, atualiza o IP
        self.clp_ip = novo_ip
        set_plc_ip(self.clp_ip)
        print("IP atualizado para:", self.clp_ip)
        self.status_label.config(text="IP atualizado", bg="#007bff")
        self.after(2000, lambda: self.update_ip_btn.config(state="normal"))
    
    def _toggle_conexao(self):
        # Antes de alternar a conexão, verifica se o IP atual é válido e a comunicação está OK
        if not self.clp_ip or not validador_de_comunicacao_to_clp(self.clp_ip):
            print("Não é possível conectar: IP inválido ou falha na comunicação")
            self.status_label.config(text="Erro", bg="#dc3545")
            return

        # Bloqueia o botão para evitar cliques repetidos
        self.toggle_button.config(state="disabled")
        self.conectado = not self.conectado
        self._atualizar_interface()
        if self.conectado:
            threading.Thread(target=reatores_main, daemon=True).start()
        else:
            set_plc_ip("")

        self.after(2000, lambda: self.toggle_button.config(state="normal"))
    
    def _atualizar_interface(self):
        if self.conectado:
            self.status_label.config(text="Conectado", bg="#28a745")
            self.toggle_button.config(text="Desconectar")
        else:
            self.status_label.config(text="Desconectado", bg="#dc3545")
            self.toggle_button.config(text="Conectar")

def main():
    app = CLPApp()
    app.mainloop()

if __name__ == "__main__":
    main()
