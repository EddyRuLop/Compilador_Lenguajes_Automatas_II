"""FASE 2. Lee el programa con los tokens y la precedencia del proyecto."""
from entrada import tokenizar
from expresiones import PRECEDENCIA
from modelos import Resultado
from reglas import TIPOS_LITERAL


class Lector:
    def __init__(self, codigo):
        avisos = Resultado()
        # Para los triplos se aceptan también los nombres de los apuntes.
        # El analizador conserva su validación estricta por separado.
        self.tokens = [t for t in tokenizar(codigo, avisos, True) if t.clase != 'SALTO']
        self.avisos = avisos.observaciones
        self.i = 0

    @property
    def actual(self):
        return self.tokens[self.i]

    def tomar(self):
        t = self.actual
        if t.clase == 'FIN':
            self.error('Fin de entrada inesperado.')
        self.i += 1
        return t.lexema

    def error(self, mensaje):
        raise ValueError(f'Línea {self.actual.linea}: {mensaje}')

    def aceptar(self, signo):
        if self.actual.lexema == signo:
            self.tomar()
            return True
        return False

    def exigir(self, signo):
        if not self.aceptar(signo):
            self.error(f'Se esperaba {signo}.')

    def nombre(self):
        if self.actual.clase not in ('ID', 'NOMBRE'):
            self.error('Se esperaba un identificador.')
        return self.tomar()

    def expresion(self, minimo=1):
        t = self.actual
        if t.lexema in ('+', '-', '!'):
            nodo = ('unario', self.tomar(), self.expresion(6))
        elif self.aceptar('('):
            nodo = self.expresion()
            self.exigir(')')
        elif t.clase == 'NOMBRE':
            nodo = self.llamada()
        elif t.clase == 'ID' or t.clase in TIPOS_LITERAL:
            nodo = ('valor', self.tomar())
        else:
            self.error('Falta un operando.')
        while self.actual.lexema != '!' and PRECEDENCIA.get(self.actual.lexema, 0) >= minimo:
            op = self.tomar()
            nodo = ('binario', op, nodo, self.expresion(PRECEDENCIA[op] + 1))
        return nodo

    def llamada(self):
        nombre = self.nombre()
        self.exigir('(')
        args = []
        if not self.aceptar(')'):
            args.append(self.expresion())
            while self.aceptar(','):
                args.append(self.expresion())
            self.exigir(')')
        return ('llamada', nombre, args)

    def bloque(self):
        self.exigir('{')
        cuerpo = self.programa()
        self.exigir('}')
        return cuerpo

    def programa(self):
        instrucciones = []
        while self.actual.clase != 'FIN' and self.actual.lexema != '}':
            if self.aceptar(';'):
                continue
            inicio = self.i
            instruccion = []
            try:
                self.instruccion(instruccion)
            except ValueError as error:
                self.avisos.append(f'Instrucción omitida (línea {self.tokens[inicio].linea}): {error}')
                self.recuperar(inicio)
            else:
                instrucciones.extend(instruccion)
        return instrucciones

    def recuperar(self, inicio):
        linea = self.tokens[inicio].linea
        profundidad = 0
        while self.actual.clase != 'FIN':
            signo = self.actual.lexema
            if profundidad == 0:
                if signo == ';':
                    self.i += 1
                    return
                if signo == '}' or (self.i > inicio and self.actual.linea > linea and signo != '{'):
                    return
            if signo == '{':
                profundidad += 1
            elif signo == '}':
                profundidad -= 1
                if profundidad == 0:
                    self.i += 1
                    return
            self.i += 1

    def instruccion(self, instrucciones):
        if self.actual.clase in ('TIPO', 'VOID'):
            self.tomar()
            nombre = self.nombre()
            if self.aceptar('('):
                params = []
                if not self.aceptar(')'):
                    while True:
                        if self.actual.clase != 'TIPO':
                            self.error('Falta el tipo del parámetro.')
                        self.tomar()
                        params.append(self.nombre())
                        if not self.aceptar(','):
                            break
                    self.exigir(')')
                instrucciones.append(('funcion', nombre, params, self.bloque()))
                return
            while True:
                if self.aceptar('='):
                    instrucciones.append(('asignar', nombre, self.expresion()))
                if not self.aceptar(','):
                    break
                nombre = self.nombre()
        elif self.aceptar('while'):
            self.exigir('(')
            condicion = self.expresion()
            self.exigir(')')
            instrucciones.append(('while', condicion, self.bloque()))
            return
        elif self.aceptar('return'):
            valor = None if self.actual.lexema in (';', '}') else self.expresion()
            instrucciones.append(('return', valor))
        elif self.actual.clase == 'NOMBRE':
            instrucciones.append(self.llamada())
        else:
            nombre = self.nombre()
            if self.actual.lexema in ('++', '--'):
                expr = ('binario', self.tomar()[0], ('valor', nombre), ('valor', '1'))
            else:
                self.exigir('=')
                expr = self.expresion()
            instrucciones.append(('asignar', nombre, expr))
        if not self.aceptar(';') and self.actual.lexema not in ('', '}'):
            if self.actual.linea == self.tokens[self.i - 1].linea:
                self.error('Falta el punto y coma.')
