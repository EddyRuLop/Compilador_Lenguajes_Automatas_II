"""Tabla de lexemas y pila de ámbitos. Las declaraciones se activan en orden."""
from reglas import TIPOS_LITERAL


class Simbolos:
    def __init__(self, tokens, resultado):
        self.resultado = resultado
        self.filas = {}
        self.filas_funciones = {}
        self.ambitos = [{}]
        self.ids_ambito = [0]
        self.siguiente_ambito = 1
        self.pendientes = {}
        self.funciones = {}  # Solo funciones declaradas hasta el punto actual.
        self.parametros = {}
        # Primera pasada: lexemas no repetidos en orden de aparición.
        i = 0
        while i < len(tokens):
            t = tokens[i]
            if t.clase not in {'SALTO', 'FIN', 'INVALIDO'}:
                if t.clase == 'NOMBRE':
                    # La función se distingue internamente; la tabla muestra
                    # únicamente su lexema, sin añadir paréntesis.
                    if t.lexema not in self.filas_funciones:
                        fila = {'Lexema': t.lexema, 'Tipo': ''}
                        self.filas_funciones[t.lexema] = fila
                        resultado.simbolos.append(fila)
                elif t.lexema not in self.filas:
                    fila = {'Lexema': t.lexema, 'Tipo': TIPOS_LITERAL.get(t.clase, '')}
                    self.filas[t.lexema] = fila
                    resultado.simbolos.append(fila)
            i += 1
        self.asignadas = set()

    def entrar(self):
        self.ambitos.append({})
        self.ids_ambito.append(self.siguiente_ambito)
        self.siguiente_ambito += 1

    def salir(self):
        if len(self.ambitos) > 1:
            self.ambitos.pop()
            self.ids_ambito.pop()

    def buscar(self, lexema):
        i = len(self.ambitos) - 1
        while i >= 0:
            if lexema in self.ambitos[i]:
                return self.ambitos[i][lexema]
            i -= 1
        return None

    def duplicada(self, lexema):
        return lexema in self.ambitos[-1]

    def fila_variable(self, lexema, ambito):
        clave = (lexema, ambito)
        if clave not in self.pendientes:
            if lexema not in self.asignadas:
                fila = self.filas[lexema]
                self.asignadas.add(lexema)
            else:
                # Igual nombre en ámbitos distintos: son símbolos diferentes.
                fila = {'Lexema': lexema, 'Tipo': ''}
                self.resultado.simbolos.append(fila)
            self.pendientes[clave] = fila
        return self.pendientes[clave]

    def marcar_indefinida(self, token):
        self.fila_variable(token.lexema, self.ids_ambito[-1])

    def declarar(self, token, tipo):
        self.ambitos[-1][token.lexema] = tipo
        self.fila_variable(token.lexema, self.ids_ambito[-1])['Tipo'] = tipo

    def tipo(self, token):
        if token.clase == 'LLAMADA':
            return self.funciones.get(token.lexema)
        if token.clase == 'ID':
            return self.buscar(token.lexema)
        return TIPOS_LITERAL.get(token.clase)
