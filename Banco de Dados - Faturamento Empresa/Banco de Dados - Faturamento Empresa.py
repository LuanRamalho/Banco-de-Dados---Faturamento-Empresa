import tkinter as tk
from tkinter import ttk, messagebox
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Banco de dados em arquivo JSON
DATABASE_FILE = "faturamento.json"

def load_data():
    try:
        with open(DATABASE_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_data(data):
    with open(DATABASE_FILE, "w") as file:
        json.dump(data, file, indent=4)

class FaturamentoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Faturamento Anual")
        self.data = load_data()
        self.setup_window1()

    def setup_window1(self):
        # Limpa a janela
        for widget in self.root.winfo_children():
            widget.destroy()

        root.configure(bg="#66FFFA")

        tk.Label(self.root, text="Faturamento Anual", font=("Arial", 20, "bold"), bg="#66FFFA", fg="blue").pack(pady=10)

        frame = tk.Frame(self.root, bg="#66FFFA")
        frame.pack(pady=10)

        tk.Label(frame, text="Ano:", bg="#66FFFA", font=("Arial",12)).grid(row=0, column=0, padx=5, pady=5)
        self.ano_entry = tk.Entry(frame, font=("Arial",12))
        self.ano_entry.grid(row=0, column=1, padx=5, pady=5)

        self.meses_entries = {}
        meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        for i, mes in enumerate(meses):
            tk.Label(frame, text=f"{mes}:", bg="#66FFFA", font=("Arial",12)).grid(row=i+1, column=0, padx=5, pady=5)
            entry = tk.Entry(frame, font=("Arial",12))
            entry.grid(row=i+1, column=1, padx=5, pady=5)
            self.meses_entries[mes] = entry

        button_frame = tk.Frame(self.root, bg="#66FFFA")
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Salvar e Continuar", command=self.save_data_window2, bg="green", fg="white", font=("Arial",12,"bold")).pack(pady=10)
        tk.Button(button_frame, text="Ver Dados Existentes", command=self.setup_window2, bg="blue", fg="white", font=("Arial",12,"bold")).pack(side=tk.LEFT, padx=5)

    def save_data_window2(self):
        ano = self.ano_entry.get()
        if not ano.isdigit():
            messagebox.showerror("Erro", "O ano deve ser um número inteiro.")
            return

        faturamento = {}
        try:
            for mes, entry in self.meses_entries.items():
                faturamento[mes] = float(entry.get())
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira valores numéricos válidos para o faturamento.")
            return

        # Salva os dados no banco
        self.data.append({"Ano": int(ano), **faturamento})
        save_data(self.data)

        # Vai para a próxima janela
        self.setup_window2()

    def setup_window2(self):
        # Limpa a janela
        for widget in self.root.winfo_children():
            widget.destroy()

        root.configure(bg="#26006B")

        tk.Label(self.root, text="Gerenciar Faturamento", font=("Arial", 20, "bold"), bg="#26006B", fg="#FEFF81").pack(pady=10)

        frame = tk.Frame(self.root, bg="#26006B")
        frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.search_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.search_var, width=50).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Buscar", command=self.search_data, bg="blue", fg="white", font=("Arial",12,"bold")).pack(side=tk.LEFT, padx=5)

        # Configuração do frame principal para a tabela e barras de rolagem
        tree_frame = tk.Frame(self.root, bg="#26006B")
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Criação da Treeview com configuração de colunas
        self.tree = ttk.Treeview(tree_frame, columns=["Ano"] + list(self.meses_entries.keys()), show="headings", height=15)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configuração das barras de rolagem
        scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        scrollbar_x = ttk.Scrollbar(self.root, orient=tk.HORIZONTAL, command=self.tree.xview)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        # Configurações das colunas
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")  # Define uma largura padrão para as colunas

        self.load_tree_data(self.data)

        button_frame = tk.Frame(self.root, bg="#26006B")
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Editar", command=self.edit_selected, bg="#936100", fg="white",font=("arial",12,"bold")).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Excluir", command=self.delete_selected, bg="#7B0000", fg="white",font=("arial",12,"bold")).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Voltar", command=self.setup_window1, bg="#787878", fg="white",font=("arial",12,"bold")).pack(side=tk.LEFT, padx=5)

    def search_data(self):
        query = self.search_var.get()
        filtered_data = [row for row in self.data if query.lower() in str(row).lower()]
        self.load_tree_data(filtered_data)

    def load_tree_data(self, data):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for row in data:
            values = list(row.values())
            self.tree.insert("", tk.END, values=values + ["Ver Gráfico"])

        self.tree.bind("<Double-1>", self.on_action_click)

    def on_action_click(self, event):
        selected_item = self.tree.focus()
        if not selected_item:
            return

        values = self.tree.item(selected_item, "values")
        ano = int(values[0])
        row_data = next((row for row in self.data if row["Ano"] == ano), None)

        if row_data:
            self.show_graph(row_data)

    def show_graph(self, data):
        window = tk.Toplevel(self.root)
        window.title(f"Faturamento {data['Ano']}")

        meses = list(data.keys())[1:]
        valores = list(data.values())[1:]

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.barh(meses, valores, color="skyblue")

        for index, value in enumerate(valores):
            ax.text(value, index, f"{value:.2f}", va="center")

        ax.set_xlabel("Faturamento")
        ax.set_ylabel("Meses")
        ax.set_title(f"Faturamento Mensal - {data['Ano']}")

        canvas = FigureCanvasTkAgg(fig, window)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        canvas.draw()

    def edit_selected(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Atenção", "Por favor, selecione um item para editar.")
            return

        values = self.tree.item(selected_item, "values")
        ano = values[0]

        edit_window = tk.Toplevel(self.root)
        edit_window.title("Editar Faturamento")

        tk.Label(edit_window, text="Ano:").grid(row=0, column=0, padx=5, pady=5)
        ano_entry = tk.Entry(edit_window)
        ano_entry.grid(row=0, column=1, padx=5, pady=5)
        ano_entry.insert(0, ano)
        ano_entry.configure(state="disabled")

        entries = {}
        for i, mes in enumerate(self.meses_entries.keys()):
            tk.Label(edit_window, text=f"{mes}:").grid(row=i+1, column=0, padx=5, pady=5)
            entry = tk.Entry(edit_window)
            entry.grid(row=i+1, column=1, padx=5, pady=5)
            entry.insert(0, values[i+1])
            entries[mes] = entry

        def save_edit():
            try:
                for mes, entry in entries.items():
                    for row in self.data:
                        if row["Ano"] == int(ano):
                            row[mes] = float(entry.get())
                save_data(self.data)
                self.load_tree_data(self.data)
                edit_window.destroy()
            except ValueError:
                messagebox.showerror("Erro", "Por favor, insira valores numéricos válidos.")

        tk.Button(edit_window, text="Salvar", command=save_edit, bg="green", fg="white").grid(row=len(self.meses_entries)+1, column=0, columnspan=2, pady=10)

    def delete_selected(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Atenção", "Por favor, selecione um item para excluir.")
            return

        values = self.tree.item(selected_item, "values")
        ano = int(values[0])

        confirm = messagebox.askyesno("Confirmar", f"Tem certeza que deseja excluir o faturamento do ano {ano}?")
        if confirm:
            self.data = [row for row in self.data if row["Ano"] != ano]
            save_data(self.data)
            self.load_tree_data(self.data)

root = tk.Tk()
app = FaturamentoApp(root)
root.mainloop()