import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3



db = sqlite3.connect("clinica.db")
c = db.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS pacientes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    idade INTEGER,
    peso REAL,
    altura REAL,
    imc REAL
)
""")

db.commit()


def limpar():
    for e in entradas:
        e.delete(0, tk.END)


def classificar_imc(imc):
    if imc < 18.5:
        return "Abaixo do peso"
    elif imc < 25:
        return "Peso normal"
    elif imc < 30:
        return "Acima do peso"
    else:
        return "Obesidade"


def cadastrar():
    try:
        nome = entradas[0].get()
        idade = int(entradas[1].get())
        peso = float(entradas[2].get())
        altura = float(entradas[3].get())

        if altura <= 0 or peso <= 0 or idade <= 0 or nome == "":
            raise ValueError

        imc = peso / (altura * altura)
        classificacao = classificar_imc(imc)

        c.execute("""
        INSERT INTO pacientes(nome, idade, peso, altura, imc)
        VALUES(?,?,?,?,?)
        """, (nome, idade, peso, altura, imc))

        db.commit()

        listar()
        limpar()

        messagebox.showinfo(
            "Sucesso",
            f"Paciente cadastrado!\n\n"
            f"IMC: {imc:.2f}\n"
            f"Classificação: {classificacao}"
        )

    except:
        messagebox.showerror(
            "Erro",
            "Preencha os dados corretamente."
        )


def listar():
    tabela.delete(*tabela.get_children())

    c.execute("SELECT * FROM pacientes")

    for paciente in c.fetchall():

        classificacao = classificar_imc(paciente[5])

        tabela.insert(
            "",
            tk.END,
            values=(
                paciente[0],
                paciente[1],
                paciente[2],
                paciente[3],
                paciente[4],
                f"{paciente[5]:.2f}",
                classificacao
            )
        )


def selecionar(event):
    item = tabela.selection()

    if item:
        dados = tabela.item(item)["values"]

        limpar()

        entradas[0].insert(0, dados[1])
        entradas[1].insert(0, dados[2])
        entradas[2].insert(0, dados[3])
        entradas[3].insert(0, dados[4])


def editar():
    item = tabela.selection()

    if not item:
        messagebox.showwarning(
            "Atenção",
            "Selecione um paciente na tabela."
        )
        return

    try:
        id_paciente = tabela.item(item)["values"][0]

        nome = entradas[0].get()
        idade = int(entradas[1].get())
        peso = float(entradas[2].get())
        altura = float(entradas[3].get())

        if altura <= 0 or peso <= 0 or idade <= 0 or nome == "":
            raise ValueError

        imc = peso / (altura * altura)
        classificacao = classificar_imc(imc)

        c.execute("""
        UPDATE pacientes
        SET nome=?, idade=?, peso=?, altura=?, imc=?
        WHERE id=?
        """, (
            nome,
            idade,
            peso,
            altura,
            imc,
            id_paciente
        ))

        db.commit()

        listar()
        limpar()

        messagebox.showinfo(
            "Sucesso",
            f"Paciente editado!\n\n"
            f"IMC: {imc:.2f}\n"
            f"Classificação: {classificacao}"
        )

    except:
        messagebox.showerror(
            "Erro",
            "Preencha os dados corretamente."
        )


def excluir():
    item = tabela.selection()

    if not item:
        messagebox.showwarning(
            "Atenção",
            "Selecione um paciente."
        )
        return

    id_paciente = tabela.item(item)["values"][0]

    resposta = messagebox.askyesno(
        "Confirmar",
        "Deseja realmente excluir este paciente?"
    )

    if resposta:
        c.execute(
            "DELETE FROM pacientes WHERE id=?",
            (id_paciente,)
        )

        db.commit()

        listar()
        limpar()

        messagebox.showinfo(
            "Sucesso",
            "Paciente excluído!"
        )


janela = tk.Tk()

janela.title("Clínica Saúde & Bem-Estar")
janela.geometry("1000x500")



tk.Label(
    janela,
    text="Cadastro de Pacientes",
    font=("Arial", 18, "bold")
).pack(pady=10)


frame = tk.Frame(janela)
frame.pack()

nomes = [
    "Nome",
    "Idade",
    "Peso (kg)",
    "Altura (m)"
]

entradas = []

for i, nome in enumerate(nomes):

    tk.Label(
        frame,
        text=nome
    ).grid(
        row=0,
        column=i,
        padx=5
    )

    entrada = tk.Entry(
        frame,
        width=18
    )

    entrada.grid(
        row=1,
        column=i,
        padx=5
    )

    entradas.append(entrada)


tk.Button(
    janela,
    text="Cadastrar",
    command=cadastrar,
    width=15
).pack(pady=5)


tk.Button(
    janela,
    text="Editar",
    command=editar,
    width=15
).pack(pady=5)


tk.Button(
    janela,
    text="Excluir",
    command=excluir,
    width=15
).pack(pady=5)


colunas = (
    "ID",
    "Nome",
    "Idade",
    "Peso",
    "Altura",
    "IMC",
    "Classificação"
)


tabela = ttk.Treeview(
    janela,
    columns=colunas,
    show="headings"
)


for coluna in colunas:

    tabela.heading(
        coluna,
        text=coluna
    )

    tabela.column(
        coluna,
        width=120
    )


tabela.pack(
    pady=15,
    fill="x"
)


tabela.bind(
    "<ButtonRelease-1>",
    selecionar
)


listar()

janela.mainloop()
