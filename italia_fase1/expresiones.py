"""Valida expresiones con pilas, sin eval, AST de Python ni recursión.

Devuelve notación postfija para comprobar condiciones while. En las
asignaciones, las reglas se verifican contra el tipo del destino (PDF I).
"""
from modelos import Token
from reglas import ARITMETICOS, RELACIONALES, LOGICOS, TIPOS_LITERAL

PRECEDENCIA = {'||': 1, '&&': 2, '==': 3, '!=': 3, '<': 3, '>': 3,
               '<=': 3, '>=': 3, '+': 4, '-': 4, '*': 5, '/': 5, '%': 5,
               'u+': 6, 'u-': 6, '!': 6}


def reconocer_llamadas(tokens, resultado):
    """/<Nombre>/ ( ) pasa a ser un operando LLAMADA; conserva nombre y posición.

    La tabla de símbolos usa los tokens originales y conserva ( y ) separados.
    Sin paréntesis, /<Nombre>/ conserva su categoría de variable.
    """
    salida, i = [], 0
    while i < len(tokens):
        t = tokens[i]
        if t.clase == 'NOMBRE':
            if i + 2 >= len(tokens) or tokens[i + 1].lexema != '(' or tokens[i + 2].lexema != ')':
                resultado.avisar(t, 'Una función se llama /<Nombre>/(); esta fase no admite argumentos.')
                return None
            salida.append(Token('LLAMADA', t.lexema, t.linea, t.columna))
            i += 3
        else:
            salida.append(t)
            i += 1
    return salida


def validar(tokens, resultado, condicion=False):
    """Retorna lista postfija o None; no admite operandos u operadores sueltos."""
    salida, pila = [], []
    espera_operando = True
    i = 0
    if not tokens:
        return None
    while i < len(tokens):
        t = tokens[i]
        valor = t.lexema
        if t.clase == 'INVALIDO':
            return None  # entrada.py ya explicó el problema.
        if t.clase in {'ID', 'LLAMADA'} or t.clase in TIPOS_LITERAL:
            if not espera_operando:
                resultado.avisar(t, 'Falta un operador entre operandos.')
                return None
            salida.append(t)
            espera_operando = False
        elif valor == '(':
            if not espera_operando:
                resultado.avisar(t, 'Falta un operador; las funciones se escriben /<Nombre>/().')
                return None
            pila.append(t)
        elif valor == ')':
            if espera_operando:
                resultado.avisar(t, 'Paréntesis vacío o falta un operando.')
                return None
            while pila and pila[-1].lexema != '(':
                salida.append(pila.pop())
            if not pila:
                resultado.avisar(t, 'Paréntesis de cierre sin apertura.')
                return None
            pila.pop()
        elif valor in ARITMETICOS | RELACIONALES | LOGICOS | {'!'}:
            if not condicion and valor in RELACIONALES | LOGICOS | {'!'}:
                resultado.avisar(t, 'Las comparaciones y operadores lógicos solo se usan en while.')
                return None
            if espera_operando:
                if valor not in {'+', '-', '!'}:
                    resultado.avisar(t, 'Falta un operando antes del operador.')
                    return None
                clave = 'u' + valor if valor in {'+', '-'} else valor
                pila.append(Token('UNARIO', clave, t.linea, t.columna))
            else:
                if valor == '!':
                    resultado.avisar(t, 'El operador ! debe ir antes de su operando.')
                    return None
                while pila and pila[-1].lexema != '(' and (
                        PRECEDENCIA[pila[-1].lexema] >= PRECEDENCIA[valor]):
                    salida.append(pila.pop())
                pila.append(t)
                espera_operando = True
        else:
            resultado.avisar(t, 'Elemento no permitido dentro de la expresión.')
            return None
        i += 1
    if espera_operando:
        resultado.avisar(tokens[-1], 'La expresión termina sin operando.')
        return None
    while pila:
        t = pila.pop()
        if t.lexema == '(':
            resultado.avisar(t, 'Falta cerrar un paréntesis.')
            return None
        salida.append(t)
    return salida
