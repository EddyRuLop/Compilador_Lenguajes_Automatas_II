"""Única estructura de control: while. Se analiza, nunca se ejecuta.

El PDF I p. 7 pide condiciones booleanas, pero no fija su descripción de
error en los PDF I–III. Los problemas de condición se explican como avisos
fuera de la tabla semántica para no atribuir frases nuevas a la maestra.
"""
from reglas import TIPOS_LITERAL, ARITMETICOS, RELACIONALES


def revisar(postfija, simbolos, resultado):
    pila = []
    i = 0
    while i < len(postfija):
        token = postfija[i]
        op = token.lexema
        if token.clase in {'ID', 'LLAMADA'} or token.clase in TIPOS_LITERAL:
            tipo = simbolos.tipo(token)
            if tipo == 'void':
                resultado.avisar(token, 'Una función void no produce un valor para la condición de while.')
                tipo = None
            pila.append(tipo)
        elif op in {'u+', 'u-', '!'}:
            tipo = pila.pop()
            esperado = {'booleano'} if op == '!' else {'phi', 'rho'}
            if tipo is not None and tipo not in esperado:
                resultado.avisar(token, 'Operando incompatible en la condición de while.')
                tipo = None
            pila.append(tipo)
        else:
            derecho, izquierdo = pila.pop(), pila.pop()
            tipo = None
            if izquierdo is None or derecho is None:
                pila.append(None)
                i += 1
                continue
            numericos = izquierdo in {'phi', 'rho'} and derecho in {'phi', 'rho'}
            textos = izquierdo == derecho == 'delta'
            if op in ARITMETICOS:
                if numericos and op != '%':
                    tipo = 'rho' if op == '/' or 'rho' in {izquierdo, derecho} else 'phi'
                elif textos and op in {'+', '-'}:
                    tipo = 'delta'
            elif op in RELACIONALES:
                if numericos or textos or (op in {'==', '!='} and izquierdo == derecho == 'booleano'):
                    tipo = 'booleano'
            elif izquierdo == derecho == 'booleano':
                tipo = 'booleano'
            if tipo is None:
                resultado.avisar(token, 'Operandos incompatibles en la condición de while.')
            pila.append(tipo)
        i += 1
    if pila and pila[0] is not None and pila[0] != 'booleano':
        resultado.avisar(postfija[0], 'La condición de while debe producir un booleano mediante una comparación.')
