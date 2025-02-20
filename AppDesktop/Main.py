import os
import sys
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

def resource_path(relative_path):
    """
    Retorna o caminho absoluto do recurso, seja em modo de desenvolvimento
    ou após empacotar com PyInstaller.
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class CLPApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Configurações da janela principal com fundo laranja
        self.title("Conexão CLP")
        self.geometry("800x600")
        self.configure(bg="#FFA500")  # Fundo laranja
        self.resizable(False, False)

        # Estado inicial
        self.conectado = False
        self.clp_ip = "192.168.0.100"

        # Configura estilos e cria o layout
        self._configurar_estilos()
        self._criar_card()

    def _configurar_estilos(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Configuração dos botões: fundo laranja e fonte em negrito
        self.style.configure("TButton",
                             font=("Segoe UI", 12, "bold"),
                             padding=10,
                             background="#FFA500",
                             foreground="white")
        self.style.map("TButton", background=[("active", "#e69500")])

        # Estilo para o título, com fundo branco para harmonizar com o card
        self.style.configure("Title.TLabel",
                             font=("Segoe UI", 24, "bold"),
                             foreground="#FFA500",
                             background="white")

        # Estilo para textos informativos
        self.style.configure("Info.TLabel",
                             font=("Segoe UI", 14),
                             background="white",
                             foreground="#333333")

    def _criar_card(self):
        # Cria um "card" central com fundo branco para destacar os controles
        self.card = tk.Frame(self, bg="white")
        self.card.place(relx=0.5, rely=0.5, anchor="center")

        # Tentativa de carregar a logo da empresa
        try:
            logo_path = resource_path(os.path.join("Img", "Logo.jpg"))
            self.logo_image = Image.open(logo_path)
            # Redimensiona a logo preservando a proporção (largura máxima de 200px)
            max_width = 200
            ratio = max_width / self.logo_image.width
            new_width = int(self.logo_image.width * ratio)
            new_height = int(self.logo_image.height * ratio)
            self.logo_image = self.logo_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(self.logo_image)
            self.logo_label = tk.Label(self.card, image=self.logo_photo, bg="white")
            self.logo_label.pack(pady=(20, 10))
        except Exception as e:
            print("Erro ao carregar logo:", e)
            self.logo_label = tk.Label(self.card, text="Logo da Empresa", font=("Segoe UI", 18, "bold"), bg="white")
            self.logo_label.pack(pady=(20, 10))

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
        update_ip_btn = ttk.Button(ip_frame, text="Atualizar IP", command=self._atualizar_ip)
        update_ip_btn.grid(row=0, column=2, padx=(0, 10), pady=5)

        # Label de status da conexão
        self.status_label = tk.Label(self.card,
                                     text="Desconectado",
                                     font=("Segoe UI", 14, "bold"),
                                     bg="#dc3545",  # Vermelho para desconectado
                                     fg="white",
                                     width=15,
                                     height=2)
        self.status_label.pack(pady=10)

        # Botão para conectar/desconectar
        self.toggle_button = ttk.Button(self.card, text="Conectar", command=self._toggle_conexao)
        self.toggle_button.pack(pady=(10, 20))

        # Rodapé
        footer_label = ttk.Label(self.card,
                                 text="© 2025 P&D SOLUÇÕES. Todos os direitos reservados.",
                                 style="Info.TLabel")
        footer_label.pack(pady=(0, 20))

    def _atualizar_ip(self):
        """Atualiza o IP do CLP com o valor digitado."""
        novo_ip = self.ip_entry.get().strip()
        if novo_ip:
            self.clp_ip = novo_ip
            print("IP atualizado para:", self.clp_ip)

    def _toggle_conexao(self):
        """Alterna o estado de conexão e atualiza a interface."""
        self.conectado = not self.conectado
        self._atualizar_interface()

    def _atualizar_interface(self):
        """Atualiza o texto e as cores do status e do botão."""
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
