"""FASE 2. Generación independiente de triplos y exportación de la tabla."""
import csv
from collections import Counter
from fase2_sintaxis import Lector


class Etiqueta:
    """Destino que se conoce cuando se alcanza su renglón."""
    def __init__(self, pendiente=''):
        self.destino = pendiente

    def __str__(self):
        return str(self.destino)


class Generador:
    def __init__(self, programa):
        self.filas = []
        self.entradas = {}
        self.parametros = {}
        self.regresos = {}
        self.valores = {}
        self.llamadas = Counter()
        self.auxiliar = 0
        self.inspeccionar(programa)

    def inspeccionar(self, nodo):
        if isinstance(nodo, list):
            for hijo in nodo:
                self.inspeccionar(hijo)
        elif isinstance(nodo, tuple):
            if nodo[0] == 'funcion':
                nombre = nodo[1]
                self.entradas[nombre] = Etiqueta()
                self.parametros[nombre] = nodo[2]
                self.regresos[nombre] = Etiqueta()
                self.valores[nombre] = Etiqueta(f'RES({nombre})')
            elif nodo[0] == 'llamada':
                self.llamadas[nodo[1]] += 1
            for hijo in nodo[1:]:
                self.inspeccionar(hijo)

    def marcar(self, etiqueta):
        etiqueta.destino = len(self.filas) + 1

    def emitir(self, objeto, fuente, operador):
        self.filas.append((objeto, fuente, operador))

    def nuevo_auxiliar(self):
        self.auxiliar += 1
        return f'AUX{self.auxiliar}'

    def expresion(self, nodo, nivel=1):
        temp = f'T{nivel}'
        if nodo[0] == 'valor':
            self.emitir(temp, nodo[1], '=')
        elif nodo[0] == 'llamada':
            self.llamar(nodo)
            self.emitir(temp, self.valores.get(nodo[1], f'RES({nodo[1]})'), '=')
        elif nodo[0] == 'unario':
            self.expresion(nodo[2], nivel)
            if nodo[1] == '-':
                self.emitir(temp, '-1', '*')
            elif nodo[1] == '!':
                self.emitir(temp, '0', '==')
        else:
            _, op, izq, der = nodo
            self.expresion(izq, nivel)
            if der[0] == 'valor':
                fuente = der[1]
            else:
                # Una función puede usar T1 en su propio cuerpo.
                guarda = None
                if contiene_llamada(der):
                    guarda = self.nuevo_auxiliar()
                    self.emitir(guarda, temp, '=')
                fuente = self.expresion(der, nivel + 1)
                if guarda:
                    self.emitir(temp, guarda, '=')
            self.emitir(temp, fuente, op)
        return temp

    def llamar(self, nodo):
        _, nombre, args = nodo
        formales = self.parametros.get(nombre, [])
        pendientes = []
        for indice, arg in enumerate(args):
            destino = formales[indice] if indice < len(formales) else f'ARG{indice+1}({nombre})'
            temporal = self.expresion(arg)
            # Evaluar todos los argumentos en el entorno del llamador.
            if len(args) > 1 and any(a[0] != 'valor' or a[1] in formales for a in args):
                guarda = self.nuevo_auxiliar()
                self.emitir(guarda, temporal, '=')
                pendientes.append((destino, guarda))
            else:
                self.emitir(destino, temporal, '=')
        for destino, fuente in pendientes:
            self.emitir(destino, fuente, '=')
        vuelta = Etiqueta()
        if self.llamadas[nombre] > 1:
            self.emitir(f'REG({nombre})', vuelta, '=')
        elif nombre in self.regresos:
            vuelta = self.regresos[nombre]
        self.emitir('', self.entradas.get(nombre, nombre), 'JMP')
        self.marcar(vuelta)

    def condicion(self, nodo, si, no):
        if nodo[:2] == ('unario', '!'):
            self.condicion(nodo[2], no, si)
        elif nodo[0] == 'binario' and nodo[1] in ('&&', '||'):
            medio = Etiqueta()
            if nodo[1] == '&&':
                self.condicion(nodo[2], medio, no)
            else:
                self.condicion(nodo[2], si, medio)
            self.marcar(medio)
            self.condicion(nodo[3], si, no)
        else:
            self.expresion(nodo)
            self.emitir('', 'TRUE', si)
            self.emitir('', 'FALSE', no)

    def bloque(self, instrucciones, funcion=None):
        for inst in instrucciones:
            clase = inst[0]
            if clase == 'asignar':
                self.emitir(inst[1], self.expresion(inst[2]), '=')
            elif clase == 'llamada':
                self.llamar(inst)
            elif clase == 'while':
                inicio, cuerpo, fin = Etiqueta(), Etiqueta(), Etiqueta()
                self.marcar(inicio)
                self.condicion(inst[1], cuerpo, fin)
                self.marcar(cuerpo)
                self.bloque(inst[2], funcion)
                self.emitir('', inicio, 'JMP')
                self.marcar(fin)
            elif clase == 'funcion':
                _, nombre, _, cuerpo = inst
                fin = Etiqueta()
                self.emitir('', fin, 'JMP')
                self.marcar(self.entradas[nombre])
                # El PDF recupera la variable de un return simple directamente.
                if cuerpo and cuerpo[-1][0] == 'return' and cuerpo[-1][1]:
                    ultimo = cuerpo[-1][1]
                    if ultimo[0] == 'valor' and contar_retornos(cuerpo) == 1:
                        self.valores[nombre].destino = ultimo[1]
                self.bloque(cuerpo, nombre)
                if not cuerpo or cuerpo[-1][0] != 'return':
                    self.salto_regreso(nombre)
                self.marcar(fin)
                if not self.llamadas[nombre]:
                    self.marcar(self.regresos[nombre])
            elif clase == 'return':
                if funcion and inst[1] and str(self.valores[funcion]).startswith('RES('):
                    self.emitir(self.valores[funcion], self.expresion(inst[1]), '=')
                if funcion:
                    self.salto_regreso(funcion)

    def salto_regreso(self, nombre):
        self.emitir('', f'REG({nombre})' if self.llamadas[nombre] > 1
                    else self.regresos[nombre], 'JMP')


def contar_retornos(cuerpo):
    return sum(1 if i[0] == 'return' else contar_retornos(i[2])
               if i[0] == 'while' else 0 for i in cuerpo)


def contiene_llamada(nodo):
    if nodo[0] == 'binario':
        return contiene_llamada(nodo[2]) or contiene_llamada(nodo[3])
    if nodo[0] == 'unario':
        return contiene_llamada(nodo[2])
    return nodo[0] == 'llamada'


def generar_triplos(codigo, modo_pdf=False, *, avisos=None):
    # modo_pdf se conserva para quienes ya usan esta función. La fase 2
    # admite ambas sintaxis sin depender del modo elegido en el analizador.
    lector = Lector(codigo)
    programa = lector.programa()
    while lector.actual.clase != 'FIN':
        lector.avisos.append(f'Línea {lector.actual.linea}: llave de cierre sin apertura.')
        lector.tomar()
        programa.extend(lector.programa())
    if avisos is not None:
        avisos.extend(lector.avisos)
    gen = Generador(programa)
    gen.bloque(programa)
    return [(i, str(obj), str(fuente), str(op))
            for i, (obj, fuente, op) in enumerate(gen.filas, 1)]


def guardar_txt(ruta, filas):
    with open(ruta, 'w', encoding='utf-8-sig', newline='') as archivo:
        tabla = csv.writer(archivo, delimiter='\t')
        tabla.writerow(('Renglón', 'Dato objeto', 'Dato fuente', 'Operador'))
        tabla.writerows(filas)
