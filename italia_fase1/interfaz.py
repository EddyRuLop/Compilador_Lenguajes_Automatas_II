"""Interfaz mínima: editor, botón, tabla de símbolos y tabla de errores."""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pathlib import Path
from tempfile import TemporaryDirectory
from fase2_triplos import generar_triplos, guardar_txt
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
    ventana.title('Compilador Italia — Análisis semántico y triplos')
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

    # FASE 2. Lee directamente el editor aunque haya errores en la fase 1.
    def exportar():
        try:
            avisos = []
            filas = generar_triplos(editor.get('1.0', 'end-1c'), avisos=avisos)
            fin = str(len(filas) + 1)
            salida = filas
            if any((op == 'JMP' and fuente == fin) or
                   (fuente in ('TRUE', 'FALSE') and op == fin)
                   for _, _, fuente, op in filas):
                salida = filas + [(int(fin), '', '', '')]
            with TemporaryDirectory() as carpeta:
                ruta = Path(carpeta) / 'triplos.txt'
                guardar_txt(ruta, salida)
                contenido = ruta.read_text(encoding='utf-8-sig')
            vista = tk.Toplevel(ventana)
            vista.title('triplos.txt')
            texto = scrolledtext.ScrolledText(vista, width=94, height=27,
                                             wrap='none', font=('Consolas', 11))
            texto.pack(fill='both', expand=True)
            # Alinear la vista sin alterar el TXT separado por tabulaciones.
            import csv
            columnas = list(csv.reader(contenido.splitlines(), delimiter='\t'))
            anchos = [max(map(len, columna)) for columna in zip(*columnas)]
            texto.insert('1.0', '\n'.join('  '.join(c.ljust(a) for c, a in zip(f, anchos))
                                         for f in columnas))
            texto.configure(state='disabled')
            if avisos:
                ttk.Label(vista, text='Salida parcial. Se omitieron instrucciones que no se pudieron interpretar.').pack(anchor='w')
                detalle = scrolledtext.ScrolledText(vista, height=5, wrap='word')
                detalle.pack(fill='x')
                detalle.insert('1.0', '\n'.join(avisos))
                detalle.configure(state='disabled')
            estado.set(f'Fase 2 · {len(filas)} triplos generados')
        except (ValueError, OSError) as error:
            messagebox.showerror('Fase 2 · Generar triplo', str(error), parent=ventana)
        except RecursionError:
            messagebox.showerror('Fase 2', 'La expresión o bloque supera el nivel de anidación admitido.', parent=ventana)

    botones = ttk.Frame(base)
    botones.pack(fill='x', pady=6)
    ttk.Button(botones, text='Analizar', command=ejecutar).pack(side='left', expand=True, fill='x')
    ttk.Button(botones, text='Generar triplo', command=exportar).pack(side='left', expand=True, fill='x')
    ttk.Label(base, textvariable=estado).pack(anchor='w', pady=(0, 5))
    contenedor.pack(fill='both', expand=True)
    ventana.mainloop()
