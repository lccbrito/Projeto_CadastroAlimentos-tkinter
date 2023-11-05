from tkinter import *
from tkinter import ttk
import sqlite3

# EXPORTAR EM PDF
from reportlab.lib.pagesizes import A4, portrait
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# CHAMAR O NAVEGADOR PADRÃO
import webbrowser

root = Tk() 

class Database:
    def connect_db(self):
        self.conn = sqlite3.connect('alimentos.bd')
        self.cursor = self.conn.cursor()

    def desconnect_db(self):
        self.conn.close()
    
    def createTable(self):
        self.connect_db(); print('Conectando ao BD')
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tabela_alimentos (
                id INTEGER PRIMARY KEY,
                nome CHAR(40) NOT NULL,
                marca CHAR(40),
                porcao REAL(10),
                kcal REAL(10),
                carboidrato REAL(10),
                proteina REAL(10),
                gordura REAL(10),
                fibra REAL(10),
                sodio REAL(10)
            );
        """)
        self.conn.commit(); print('BANCO DE DADOS CRIADO')
        self.desconnect_db()

class Buttons:
    def __init__(self, db: Database):
        self.db = db

    def clean_entries(self):
        self.id_entry.delete(0, END)
        self.nome_entry.delete(0, END)
        self.marca_entry.delete(0, END)
        self.porcao_entry.delete(0, END)
        self.kcal_entry.delete(0, END)
        self.carboidrato_entry.delete(0, END)
        self.proteina_entry.delete(0, END)
        self.gordura_entry.delete(0, END)
        self.fibra_entry.delete(0, END)
        self.sodio_entry.delete(0, END)
    
    def add_food(self):
        self.variables()
        
        self.db.connect_db()
        self.db.cursor.execute(""" INSERT INTO tabela_alimentos (nome, marca, porcao, kcal, carboidrato, proteina,gordura, fibra, sodio)
                        VALUES (?,?,?,?,?,?,?,?,?)""", (self.nome, self.marca, self.porcao, self.kcal, self.carboidrato, self.proteina, self.gordura, self.fibra, self.sodio))
        
        self.db.conn.commit()
        self.db.desconnect_db()
        self.select_list()
        self.clean_entries()

    def select_list(self):
        self.listFood.delete(*self.listFood.get_children())
        self.db.connect_db()
        list = self.db.cursor.execute("""SELECT id, nome, marca, porcao, kcal, carboidrato, proteina, gordura, fibra, sodio FROM tabela_alimentos ORDER BY id ASC;""")

        for i in list:
            self.listFood.insert("", END, values=i)
        self.db.desconnect_db()

    def variables(self):
        self.id = self.id_entry.get()
        self.nome = self.nome_entry.get()
        self.marca = self.marca_entry.get()
        self.porcao = self.porcao_entry.get()
        self.kcal = self.kcal_entry.get()
        self.carboidrato = self.carboidrato_entry.get()
        self.proteina = self.proteina_entry.get()
        self.gordura = self.gordura_entry.get()
        self.fibra = self.fibra_entry.get()
        self.sodio = self.sodio_entry.get()

    def OnDoubleClick(self, event): 
        self.clean_entries()
        self.listFood.selection()

        for n in self.listFood.selection():
            col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = self.listFood.item(n, 'values')
            self.id_entry.insert(END, col1)
            self.nome_entry.insert(END, col2)
            self.marca_entry.insert(END, col3)
            self.porcao_entry.insert(END, col4)
            self.kcal_entry.insert(END, col5)
            self.carboidrato_entry.insert(END, col6)
            self.proteina_entry.insert(END, col7)
            self.gordura_entry.insert(END, col8)
            self.fibra_entry.insert(END, col9)
            self.sodio_entry.insert(END, col10)

    def update_food(self):
        self.variables()
        self.db.connect_db()
        self.db.cursor.execute(""" UPDATE tabela_alimentos SET nome = ?, marca = ?, porcao = ?, kcal = ?, carboidrato = ?, proteina = ?, gordura = ?, fibra = ?, sodio = ? WHERE id = ?""", (self.nome, self.marca, self.porcao, self.kcal, self.carboidrato, self.proteina, self.gordura, self.fibra, self.sodio, self.id))
        self.db.conn.commit()
        self.db.desconnect_db()
        self.select_list()
        self.clean_entries()

    def delete_food(self):
        self.variables()
        self.db.connect_db()
        self.db.cursor.execute("""DELETE FROM tabela_alimentos WHERE id = ? """, (self.id,))
        self.db.conn.commit()
        self.db.desconnect_db()
        self.clean_entries()
        self.select_list()

    def search_food(self):
        self.db.connect_db()
        self.listFood.delete(*self.listFood.get_children())
        
        nome = self.nome_entry.get()
        id = self.id_entry.get()

        query = "SELECT id, nome, marca, porcao, kcal, carboidrato, proteina, gordura, fibra, sodio FROM tabela_alimentos WHERE 1=1"
        params = []  # Lista para armazenar os parâmetros da consulta

        if nome:
            query += " AND nome LIKE ?"
            params.append(f"%{nome}%")
        
        if id:
            query += " AND id LIKE ?"
            params.append(f"%{id}%")
        
        query += " ORDER BY id, nome ASC"

        self.db.cursor.execute(query, params)
        searchNameFood = self.db.cursor.fetchall()

        for i in searchNameFood:
            self.listFood.insert("", END, values=i)

        self.clean_entries()
        self.db.desconnect_db()

class Report:
    def __init__(self, bt: Buttons):
        self.bt = bt

    def generateReport(self):
        elements = []

        # Criar PDF no formato A4 retrato
        doc = SimpleDocTemplate("alimentos.pdf")

        data = [
            ['ID', 'Nome', 'Marca', 'Porção (g)', 'Valor Energético (kcal)', 'Carboidratos (g)', 'Proteínas (g)', 'Gorduras (g)', 'Fibras (g)', 'Sódio (mg)']
        ]

        self.bt.db.connect_db()
        query = "SELECT id, nome, marca, porcao, kcal, carboidrato, proteina, gordura, fibra, sodio FROM tabela_alimentos ORDER BY id ASC"
        self.bt.db.cursor.execute(query)
        data += self.bt.db.cursor.fetchall()
        self.bt.db.desconnect_db()

        # Tamanho das colunas da tabela
        col_widths = [25, 100, 50, 45, 84, 64, 54, 52, 42, 47]
    
        # Reduzir o tamanho da fonte
        styles = getSampleStyleSheet()
        custom_style = ParagraphStyle(name='Custom', parent=styles['Normal'])
        custom_style.fontName = 'Helvetica'
        custom_style.alignment = 1  # Centralizar texto
        custom_style.fontSize = 7

        table_data = []

        # Adicione o cabeçalho
        for item in data:
            row_data = []
            for value in item:
                p = Paragraph(str(value), custom_style)  # Converter para string
                row_data.append(p)
            table_data.append(row_data)

        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 2),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(Paragraph("Alimentos Cadastrados", getSampleStyleSheet()['Title']))
        elements.append(Spacer(1, 20))  # espaço em branco de 20 pontos
        elements.append(table)

        doc.topMargin = 30

        doc.build(elements)

        # Abrir o PDF no browser após a criação
        webbrowser.open('alimentos.pdf')

class App:
    def __init__(self, db: Database, bt: Buttons, rep: Report):
        self.db = db
        self.bt = bt
        self.rep = rep
        self.root = root
        self.cores()
        self.screen()
        self.screenFrames()
        self.head()
        self.foodList()
        self.db.createTable()
        self.bt.select_list()
        self.Menus()
        root.mainloop()

    def cores(self):
        self.bgScreen = '#F0F0F0' #'#1C333E'
        self.bordaFrame = '#CCCCCC' #'#759fe6'
        self.bgFrame = '#F0F0F0' #'#DFE3EE'
        self.button = '#646464' ##107db2

    def screen(self):
        self.root.title('CADASTRO DE ALIMENTOS')
        self.root.configure(background=self.bgScreen)
        self.root.geometry('1200x600')
        self.root.resizable(True, True)
        self.root.minsize(width=800, height=600)
    
    def screenFrames(self):
        # highlightbackground → borda do frame, highlightthickness → largura da borda
        self.frame_1 = Frame(self.root, bd=4, bg=self.bgFrame, highlightbackground=self.bordaFrame, highlightthickness=0.5) 
        self.frame_1.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.30)
        
        self.frame_2 = Frame(self.root, bd=4, bg=self.bgFrame, highlightbackground=self.bordaFrame, highlightthickness=0.5) 
        self.frame_2.place(relx=0.02, rely=0.33, relwidth=0.96, relheight=0.65)

    def head(self):
        # TÍTULO
        font = ('Helvetica', 20, 'bold')
        title = Label(root, text="Cadastro de Alimentos", font=font)
        title.pack(pady=21)

        # BOTÕES
        # Botão Limpar
        self.bt_limpar = Button(self.frame_1, text='Limpar', bd=2, bg=self.button, fg='white', font=('verdana', 8, 'bold'), command=self.bt.clean_entries)
        self.bt_limpar.place(relx=0.25, rely=0.4, relwidth=0.1, relheight=0.15)
       
        # Botão Buscar
        self.bt_buscar = Button(self.frame_1, text='Buscar', bd=2, bg=self.button, fg='white', font=('verdana', 8, 'bold'), command=self.bt.search_food)
        self.bt_buscar.place(relx=0.35, rely=0.4, relwidth=0.1, relheight=0.15)
        
        # Botão Novo
        self.bt_novo = Button(self.frame_1, text='Novo', bd=2, bg =self.button, fg='white', font=('verdana', 8, 'bold'), command=self.bt.add_food)
        self.bt_novo.place(relx=0.45, rely=0.4, relwidth=0.1, relheight=0.15)
        
        # Botão Alterar
        self.bt_alterar = Button(self.frame_1, text='Alterar', bd=2, bg=self.button, fg='white', font=('verdana', 8, 'bold'), command=self.bt.update_food)
        self.bt_alterar.place(relx=0.55, rely=0.4, relwidth=0.1, relheight=0.15)
       
        # Botão Excluir
        self.bt_excluir = Button(self.frame_1, text='Excluir', bd=2, bg=self.button, fg='white', font=('verdana', 8, 'bold'), command=self.bt.delete_food)
        self.bt_excluir.place(relx=0.65, rely=0.4, relwidth=0.1, relheight=0.15)

        # CRIAÇÃO DAS LABEL E ENTRADAS
        # Id
        self.lb_id = Label(self.frame_1, text="ID", bd=1, bg=self.button, fg='white')
        self.lb_id.place(relx=0.01, rely=0.7, relwidth=0.032, relheight=0.1)
        self.bt.id_entry = Entry(self.frame_1, bd=1, bg=self.bgScreen)
        self.bt.id_entry.place(relx=0.01, rely=0.8, relwidth=0.0325, relheight=0.14)
        
        # Nome do alimento
        self.lb_nome = Label(self.frame_1, text="Nome do alimento", bd=1, bg=self.button, fg='white')
        self.lb_nome.place(relx=0.05, rely=0.7,  relwidth=0.25, relheight=0.1)
        self.bt.nome_entry = Entry(self.frame_1, bd=1, bg=self.bgScreen)
        self.bt.nome_entry.place(relx=0.05, rely=0.8, relwidth=0.25, relheight=0.14)
       
        # Marca do alimento
        self.lb_marca = Label(self.frame_1, text="Marca do alimento", bd=1, bg=self.button, fg='white')
        self.lb_marca.place(relx=0.3078, rely=0.7,  relwidth=0.1, relheight=0.1)
        self.bt.marca_entry = Entry(self.frame_1, bd=1, bg=self.bgScreen)
        self.bt.marca_entry.place(relx=0.3078, rely=0.8, relwidth=0.1, relheight=0.14)
       
        # Porção
        self.lb_porcao = Label(self.frame_1, text="Porção (g)", bd=1, bg=self.button, fg='white')
        self.lb_porcao.place(relx=0.416, rely=0.7,  relwidth=0.06, relheight=0.1)
        self.bt.porcao_entry = Entry(self.frame_1, bd=1, bg=self.bgScreen)
        self.bt.porcao_entry.place(relx=0.416, rely=0.8, relwidth=0.06, relheight=0.14)
        
        # Valor energético (kcal)
        self.lb_kcal = Label(self.frame_1, text="Valor energético (kcal)", bg=self.button, fg='white')
        self.lb_kcal.place(relx=0.484, rely=0.7,  relwidth=0.12, relheight=0.1)
        self.bt.kcal_entry = Entry(self.frame_1, bd=1, bg=self.bgScreen)
        self.bt.kcal_entry.place(relx=0.484, rely=0.8, relwidth=0.12, relheight=0.14)
        
        # Carboidratos (g)
        self.lb_carboidrato = Label(self.frame_1, text="Carboidratos (g)", bg=self.button, fg='white')
        self.lb_carboidrato.place(relx=0.612, rely=0.7,  relwidth=0.09, relheight=0.1)
        self.bt.carboidrato_entry = Entry(self.frame_1, bd=1, bg=self.bgScreen)
        self.bt.carboidrato_entry.place(relx=0.612, rely=0.8, relwidth=0.09, relheight=0.14)
        
        # Proteínas (g)
        self.lb_proteina = Label(self.frame_1, text="Proteínas (g)", bg=self.button, fg='white')
        self.lb_proteina.place(relx=0.71, rely=0.7,  relwidth=0.07, relheight=0.1)
        self.bt.proteina_entry = Entry(self.frame_1, bd=1, bg=self.bgScreen)
        self.bt.proteina_entry.place(relx=0.71, rely=0.8, relwidth=0.07, relheight=0.14)
        
        # Gorduras (g)
        self.lb_gordura = Label(self.frame_1, text="Gorduras (g)", bg=self.button, fg='white')
        self.lb_gordura.place(relx=0.788, rely=0.7,  relwidth=0.07, relheight=0.1)
        self.bt.gordura_entry = Entry(self.frame_1, bd=1, bg=self.bgScreen)
        self.bt.gordura_entry.place(relx=0.788, rely=0.8, relwidth=0.07, relheight=0.14)
        
        # Fibras (g)
        self.lb_fibra = Label(self.frame_1, text="Fibras (g)", bg=self.button, fg='white')
        self.lb_fibra.place(relx=0.865, rely=0.7,  relwidth=0.05, relheight=0.1)
        self.bt.fibra_entry = Entry(self.frame_1, bd=1, bg=self.bgScreen)
        self.bt.fibra_entry.place(relx=0.865, rely=0.8, relwidth=0.05, relheight=0.14)
        
        # Sódio (mg)
        self.lb_sodio = Label(self.frame_1, text="Sódio (mg)", bg=self.button, fg='white')
        self.lb_sodio.place(relx=0.923, rely=0.7,  relwidth=0.056, relheight=0.1)
        self.bt.sodio_entry = Entry(self.frame_1, bd=1, bg=self.bgScreen)
        self.bt.sodio_entry.place(relx=0.923, rely=0.8, relwidth=0.056, relheight=0.14)

    def foodList(self):
        style = ttk.Style(self.root)
        style.theme_use('default') #default, classic
        style.configure("Treeview.Heading", background='#646464', foreground='white',  relief='flat', padding=[1, 2])

        self.bt.listFood = ttk.Treeview(self.frame_2, height=4, column=('col1', 'col2', 'col3', 'col4', 'col5', 'col6', 'col7', 'col8', 'col9', 'col10'))

        self.bt.listFood.heading('#1', text='ID')
        self.bt.listFood.heading('#2', text='Nome do alimento')
        self.bt.listFood.heading('#3', text='Marca do alimento')
        self.bt.listFood.heading('#4', text='Porção (g)')
        self.bt.listFood.heading('#5', text='Valor energético (kcal)')
        self.bt.listFood.heading('#6', text='Carboidratos (g)')
        self.bt.listFood.heading('#7', text='Proteínas (g)')
        self.bt.listFood.heading('#8', text='Gorduras (g)')
        self.bt.listFood.heading('#9', text='Fibras (g)')
        self.bt.listFood.heading('#10', text='Sódio (mg)')

        self.bt.listFood.column('#0', width=0, stretch=NO)  # Exclui a coluna 0
        self.bt.listFood.column('#1', width=5)
        self.bt.listFood.column('#2', width=160)
        self.bt.listFood.column('#3', width=80)
        self.bt.listFood.column('#4', width=25)
        self.bt.listFood.column('#5', width=70)
        self.bt.listFood.column('#6', width=45)
        self.bt.listFood.column('#7', width=40)
        self.bt.listFood.column('#8', width=35)
        self.bt.listFood.column('#9', width=20)
        self.bt.listFood.column('#10', width=20)

        self.bt.listFood.place(relx=0.01, rely=0.03, relwidth=0.97, relheight=0.93)

        self.scroolista = Scrollbar(self.frame_2, orient='vertical')
        self.bt.listFood.configure(yscrollcommand=self.scroolista.set)
        self.scroolista.place(relx=0.98, rely=0.03, relwidth=0.02, relheight=0.93)

        self.bt.listFood.bind("<Double-1>", self.bt.OnDoubleClick)

    def Menus(self):
        menubar = Menu(self.root) #background='gray', fg='#F0F0F0'
        self.root.config(menu=menubar)
        filemenu = Menu(menubar, tearoff= 0)
        filemenu2 = Menu(menubar, tearoff= 0)

        def Quit():
            self.root.destroy()
        
        menubar.add_cascade(label='Opções', menu= filemenu)
        menubar.add_cascade(label='Outros', menu= filemenu2)

        filemenu.add_command(label='Sair', command=Quit)
        filemenu2.add_command(label='Gerar lista de cadastrados', command=self.rep.generateReport)


db = Database()
bt = Buttons(db)
rep = Report(bt)
App(db, bt, rep)