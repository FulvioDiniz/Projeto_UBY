import os
import sys
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading

current_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.clp import validador_de_comunicacao_to_clp
from config.settings import set_plc_ip, get_plc_ip
from main import main as reatores_main

ADMIN_PASSWORD = "admin123"

def resource_path(relative_path):
    """Retorna o caminho absoluto do recurso relativo a este script."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

class CLPApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Conexão CLP")
        self.configure(bg="white")
        self.resizable(False, False)
        
        self.conectado = False
        self.esta_rodando = False
        self.clp_ip = get_plc_ip() or ''
        self.admin_password = ADMIN_PASSWORD

        self._configurar_estilos()

        # Container principal usando pack
        self.container = tk.Frame(self, bg="white")
        self.container.pack(expand=True, fill="both", padx=20, pady=20)

        self._criar_layout_base()
        self._criar_widgets_conteudo()

        # Força um tamanho maior para a janela
        forced_width = 900
        forced_height = 600
        self.geometry(f"{forced_width}x{forced_height}")
        
        # Centraliza a janela na tela
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w // 2) - (forced_width // 2)
        y = (screen_h // 2) - (forced_height // 2)
        self.geometry(f"+{x}+{y}")

        self._atualizar_tabela_status()

    def _configurar_estilos(self):
        """Configura estilos de botões, rótulos e Treeview."""
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Configuração dos botões com texto centralizado
        self.style.configure(
            "TButton",
            font=("Segoe UI", 12, "bold"),
            padding=10,
            background="#FFA500",
            foreground="white",
            anchor="center",    # Centraliza o conteúdo
            justify="center"    # Centraliza o texto
        )
        self.style.map("TButton", background=[("active", "#e69500")])

        self.style.configure(
            "Gear.TButton",
            background="white",
            borderwidth=0,
            focusthickness=0,
            highlightthickness=0,
            anchor="center",
            justify="center"
        )
        self.style.map(
            "Gear.TButton",
            background=[("active", "#e0e0e0")],
            relief=[("pressed", "flat")]
        )

        self.style.configure(
            "Title.TLabel",
            font=("Segoe UI", 24, "bold"),
            foreground="#FFA500",
            background="white"
        )
        self.style.configure(
            "Info.TLabel",
            font=("Segoe UI", 14),
            background="white",
            foreground="#333333"
        )

        self.style.configure(
            "Custom.Treeview",
            font=("Segoe UI", 14),
            background="white",
            fieldbackground="white",
            foreground="black",
            rowheight=40,
            bordercolor="lightgray",
            borderwidth=1
        )
        self.style.configure(
            "Custom.Treeview.Heading",
            background="#FFA500",
            foreground="white",
            font=("Segoe UI", 16, "bold")
        )
        self.style.map("Custom.Treeview.Heading",
                       background=[("active", "#e69500")])

    def _criar_layout_base(self):
        """Cria a estrutura base com pack."""
        # Label de ERRO
        self.error_label = tk.Label(
            self.container,
            text="",
            bg="white",
            fg="red",
            font=("Segoe UI", 12, "bold")
        )
        self.error_label.pack(side="top", fill="x", pady=(0, 10))

    def _criar_widgets_conteudo(self):
        # Frame do Card (lado esquerdo)
        self.card = tk.Frame(self.container, bg="white", width=380)
        self.card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        pad_frame = tk.Frame(self.card, bg="white")
        pad_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Logo
        try:
            logo_path = resource_path(os.path.join("img", "Logo.jpg"))
            logo_image = Image.open(logo_path)
            max_width = 200
            ratio = max_width / logo_image.width
            new_size = (int(logo_image.width * ratio), int(logo_image.height * ratio))
            logo_image = logo_image.resize(new_size, Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = tk.Label(pad_frame, image=self.logo_photo, bg="white")
            logo_label.pack(pady=(20, 10))
        except Exception as e:
            print("Erro ao carregar logo:", e)
            logo_label = tk.Label(pad_frame, text="Logo da Empresa",
                                  font=("Segoe UI", 18, "bold"), bg="white")
            logo_label.pack(pady=(20, 10))
        
        # Título
        self.title_label = ttk.Label(pad_frame, text="Conexão CLP", style="Title.TLabel")
        self.title_label.pack(pady=(0, 20))
        
        # IP atual (rótulo)
        ip_frame = tk.Frame(pad_frame, bg="white")
        ip_frame.pack(pady=10, padx=20)

        ip_label = ttk.Label(ip_frame, text="IP do CLP:", style="Info.TLabel")
        ip_label.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="e")

        self.ip_val_label = ttk.Label(ip_frame, text=self.clp_ip, style="Info.TLabel")
        self.ip_val_label.grid(row=0, column=1, padx=(0, 10), pady=5, sticky="w")
        
        # Botão Conectar/Desconectar com texto centralizado
        self.toggle_button = ttk.Button(pad_frame, text="Conectar", command=self._toggle_conexao)
        self.toggle_button.pack(pady=(10, 20))

        # Frame da direita (tabela de status)
        self.status_frame = tk.Frame(self.container, bg="white", width=400)
        self.status_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        st_pad_frame = tk.Frame(self.status_frame, bg="white")
        st_pad_frame.pack(fill="both", expand=True, padx=20, pady=20)

        status_title = ttk.Label(st_pad_frame, text="Tabela de Status", style="Title.TLabel")
        status_title.pack(pady=(0, 10))

        self.status_tree = ttk.Treeview(
            st_pad_frame, 
            columns=("param", "valor"), 
            show="headings", 
            style="Custom.Treeview", 
            height=5
        )
        self.status_tree.heading("param", text="Parâmetro")
        self.status_tree.heading("valor", text="Valor")
        
        self.status_tree.column("param", minwidth=150, width=160, anchor="center", stretch=True)
        self.status_tree.column("valor", minwidth=150, width=160, anchor="center", stretch=True)

        self.status_tree.pack(pady=10, fill="x")

        self.status_tree.insert("", "end", iid="ip", values=("IP", self.clp_ip))
        self.status_tree.insert("", "end", iid="conexao", values=("Conexão", "Desconectado"))
        self.status_tree.insert("", "end", iid="execucao", values=("Execução", "Parado"))

        self.status_tree.tag_configure("conectado", background="#d4edda", foreground="#155724")
        self.status_tree.tag_configure("desconectado", background="#f8d7da", foreground="#721c24")

        # Botão Engrenagem
        gear_path = resource_path(os.path.join("img", "gear.png"))
        try:
            gear_image = Image.open(gear_path)
            gear_image = gear_image.resize((32, 32), Image.Resampling.LANCZOS)
            self.gear_photo = ImageTk.PhotoImage(gear_image)
        except:
            self.gear_photo = None

        self.config_button = ttk.Button(
            self,
            image=self.gear_photo,
            command=self._abrir_configuracoes,
            style="Gear.TButton"
        )
        if not self.gear_photo:
            self.config_button.config(text="Config")

        # Posiciona a engrenagem no canto
        self.config_button.place(x=5, y=5)
        self.config_button.lift()

    def _atualizar_tabela_status(self):
        self.status_tree.set("ip", "valor", self.clp_ip)
        self.ip_val_label.config(text=self.clp_ip)

        if self.conectado:
            self.status_tree.set("conexao", "valor", "Conectado")
            self.status_tree.item("conexao", tags=("conectado",))
        else:
            self.status_tree.set("conexao", "valor", "Desconectado")
            self.status_tree.item("conexao", tags=("desconectado",))

        if self.esta_rodando:
            self.status_tree.set("execucao", "valor", "Rodando")
            self.status_tree.item("execucao", tags=("conectado",))
        else:
            self.status_tree.set("execucao", "valor", "Parado")
            self.status_tree.item("execucao", tags=("desconectado",))

    def _abrir_configuracoes(self):
        config_dialog = tk.Toplevel(self)
        config_dialog.title("Configurações")
        config_dialog.geometry("400x300")
        config_dialog.resizable(False, False)
        config_dialog.grab_set()

        frm = tk.Frame(config_dialog, padx=20, pady=20)
        frm.pack(expand=True, fill="both")

        lbl_senha_atual = ttk.Label(frm, text="Senha de Administrador:", font=("Segoe UI", 12))
        lbl_senha_atual.pack(pady=(0, 5), anchor="w")

        senha_atual_entry = ttk.Entry(frm, show="*", font=("Segoe UI", 12))
        senha_atual_entry.pack(pady=(0, 10), fill="x")

        lbl_novo_ip = ttk.Label(frm, text="Novo IP:", font=("Segoe UI", 12))
        novo_ip_entry = ttk.Entry(frm, font=("Segoe UI", 12))

        def validar_senha():
            pwd_informada = senha_atual_entry.get().strip()
            if pwd_informada == self.admin_password:
                senha_atual_entry.config(state="disabled")
                btn_verificar.config(state="disabled")
                lbl_novo_ip.pack(pady=(10, 5), anchor="w")
                novo_ip_entry.pack(pady=(0, 10), fill="x")
                novo_ip_entry.insert(0, self.clp_ip)
                btn_salvar.pack(pady=10)
            else:
                print("Senha incorreta!")

        btn_verificar = ttk.Button(frm, text="Verificar", command=validar_senha)
        btn_verificar.pack(pady=(0, 10))

        def salvar_alteracoes():
            novo_ip = novo_ip_entry.get().strip()
            if novo_ip:
                self.clp_ip = novo_ip
                set_plc_ip(self.clp_ip)
                print(f"IP atualizado para: {self.clp_ip}")
            self._atualizar_tabela_status()
            config_dialog.destroy()

        btn_salvar = ttk.Button(frm, text="Salvar", command=salvar_alteracoes)
        # Note que o botão "Salvar" só será exibido após a verificação da senha

    def _toggle_conexao(self):
        self.error_label.config(text="")

        # Validação
        if not self.clp_ip or not validador_de_comunicacao_to_clp(self.clp_ip):
            self.error_label.config(text="Falha ao conectar: IP inválido ou sem comunicação.")
            print("Não é possível conectar: IP inválido ou falha na comunicação")
            return
        
        self.toggle_button.config(state="disabled")
        self.conectado = not self.conectado
        
        if self.conectado:
            self.esta_rodando = True
            threading.Thread(target=reatores_main, daemon=True).start()
            self.toggle_button.config(text="Desconectar")
        else:
            self.esta_rodando = False
            set_plc_ip("")
            self.toggle_button.config(text="Conectar")

        self._atualizar_tabela_status()
        # Reativa o botão depois de 2 segundos
        self.after(2000, lambda: self.toggle_button.config(state="normal"))

def main():
    app = CLPApp()
    app.mainloop()

if __name__ == "__main__":
    main()
