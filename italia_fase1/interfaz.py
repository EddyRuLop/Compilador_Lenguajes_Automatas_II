"""Interfaz mínima: editor, botón, tabla de símbolos y tabla de errores."""
import tkinter as tk
from tkinter import ttk, scrolledtext
from analizador import analizar


def crear_tabla(padre, titulo, columnas, anchos):
    marco = ttk.LabelFrame(padre, text=titulo, padding=5)
    tabla = ttk.Treeview(marco, columns=columnas, show='headings')
    i = 0
    while i < len(columnas):
        tabla.heading(columnas[i], text=columnas[i])
        tabla.column(columnas[i], width=anchos[i], minwidth=50)
        i += 1
    vertical = ttk.Scrollbar(marco, orient='vertical', command=tabla.yview)
    horizontal = ttk.Scrollbar(marco, orient='horizontal', command=tabla.xview)
    tabla.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
    marco.rowconfigure(0, weight=1)
    marco.columnconfigure(0, weight=1)
    tabla.grid(row=0, column=0, sticky='nsew')
    vertical.grid(row=0, column=1, sticky='ns')
    horizontal.grid(row=1, column=0, sticky='ew')
    return marco, tabla


def llenar(tabla, filas):
    hijos = tabla.get_children()
    if hijos:
        tabla.delete(*hijos)
    columnas = tabla['columns']
    i = 0
    while i < len(filas):
        valores, j = [], 0
        while j < len(columnas):
            valores.append(filas[i][columnas[j]])
            j += 1
        tabla.insert('', 'end', values=valores)
        i += 1


def iniciar():
    ventana = tk.Tk()
    ventana.title('Compilador Italia — Fase 1')
    ventana.geometry('1100x700')
    ventana.minsize(800, 500)
    base = ttk.Frame(ventana, padding=8)
    base.pack(fill='both', expand=True)
    editor = scrolledtext.ScrolledText(base, height=13, font=('Consolas', 11))
    editor.pack(fill='both', expand=True)
    estado = tk.StringVar(value='Escribe o pega el código y pulsa Analizar.')
    contenedor = ttk.Frame(base)
    contenedor.columnconfigure(0, weight=1)
    contenedor.columnconfigure(1, weight=2)
    contenedor.rowconfigure(0, weight=1)
    marco_s, tabla_s = crear_tabla(contenedor, 'Tabla de símbolos', ('Lexema', 'Tipo'), (160, 80))
    marco_e, tabla_e = crear_tabla(contenedor, 'Tabla de errores',
                                 ('Token', 'Lexema', 'Renglón', 'Descripción'), (85, 130, 60, 270))
    marco_s.grid(row=0, column=0, sticky='nsew', padx=(0, 4))
    marco_e.grid(row=0, column=1, sticky='nsew')

    def ejecutar():
        resultado = analizar(editor.get('1.0', 'end-1c'))
        llenar(tabla_s, resultado.simbolos)
        llenar(tabla_e, resultado.errores)
        estado.set(f'{len(resultado.errores)} errores semánticos. '
                   f'{len(resultado.observaciones)} observaciones de entrada.')
        if resultado.observaciones:
            # Fuera de la tabla: las diapositivas no asignan descripciones
            # exactas para errores léxicos/sintácticos o condiciones inválidas.
            aviso = tk.Toplevel(ventana)
            aviso.title('Errores de entrada — escritura o estructura')
            texto = scrolledtext.ScrolledText(aviso, width=90, height=15, wrap='word')
            texto.pack(fill='both', expand=True)
            texto.insert('1.0', '\n'.join(resultado.observaciones))
            texto.configure(state='disabled')

    ttk.Button(base, text='Analizar', command=ejecutar).pack(fill='x', pady=6)
    ttk.Label(base, textvariable=estado).pack(anchor='w', pady=(0, 5))
    contenedor.pack(fill='both', expand=True)
    ventana.mainloop()
