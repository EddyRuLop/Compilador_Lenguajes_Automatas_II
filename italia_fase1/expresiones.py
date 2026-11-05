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
    """Agrupa llamadas y sus argumentos con una pila, incluso si están anidadas.

    La tabla de símbolos usa los tokens originales y conserva ( y ) separados.
    Sin paréntesis, /<Nombre>/ conserva su categoría de variable.
    """
    salida, pila = [], []
    for t in tokens:
        if t.clase == 'NOMBRE':
            salida.append(t)
        elif t.lexema == '(':
            nombre = salida.pop() if salida and salida[-1].clase == 'NOMBRE' else None
            pila.append((salida, nombre, []))
            salida = []
        elif t.lexema == ',' and pila and pila[-1][1] is not None:
            if validar(salida, resultado) is None:
                if not salida:
                    resultado.avisar(t, 'Falta un argumento antes de la coma.')
                return None
            pila[-1][2].append(salida)
            salida = []
        elif t.lexema == ')' and pila:
            anterior, nombre, args = pila.pop()
            if nombre is None:
                anterior.extend([Token('SIMBOLO', '(', t.linea, t.columna), *salida, t])
            else:
                if salida or args:
                    if validar(salida, resultado) is None:
                        if not salida:
                            resultado.avisar(t, 'Falta un argumento después de la coma.')
                        return None
                    args.append(salida)
                anterior.append(Token('LLAMADA', nombre.lexema, nombre.linea,
                                      nombre.columna, args))
            salida = anterior
        else:
            salida.append(t)
    if pila:
        resultado.avisar(tokens[-1], 'Falta cerrar un paréntesis.')
        return None
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
