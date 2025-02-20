import tkinter as tk
from app.clp import write_clp
from app.database import insert_to_db

def update_value(plc_ip):
    tag_name = 'Param_Reator_05.Product_Name'
    new_value = entry_value.get()

    if new_value:
        if write_clp(tag_name, new_value, plc_ip):
            print(f"Novo valor escrito no CLP: {new_value}")
            insert_to_db(tag_name, new_value)
        else:
            print("Erro ao escrever no CLP.")

def open_window(plc_ip):
    global entry_value

    root = tk.Tk()
    root.title("Modificador de Valor da Tag")

    label = tk.Label(root, text="Digite o novo valor:")
    label.pack(pady=10)

    entry_value = tk.Entry(root)
    entry_value.pack(pady=5)

    update_button = tk.Button(root, text="Enviar", command=lambda: update_value(plc_ip))
    update_button.pack(pady=10)

    root.mainloop()
