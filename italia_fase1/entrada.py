"""Capa de entrada: reconoce lexemas completos y conserva sus posiciones.

Los PDF I–III no dan un catálogo de errores léxicos/sintácticos. Esta capa
produce observaciones de entrada, no inventa tokens ErrLex/ErrSyn.
"""
import re
from modelos import Token
from reglas import TIPOS

IDENTIFICADOR = re.compile(r'/<[a-zA-Z0-9]+>/\Z')
NUMERO = re.compile(r'[0-9]+(?:\.[0-9]+)?\Z')
DOBLES = {'==', '!=', '<=', '>=', '&&', '||', '++', '--'}
SIMPLES = set('=,+-*/%(){};<>!')
MAX_CARACTERES = 250_000
MAX_TOKENS = 50_000


def tokenizar(codigo, resultado, modo_pdf=False):
    """Siempre consume caracteres: incluso una entrada inválida hace avanzar."""
    tokens = []
    i, linea, columna = 0, 1, 1
    codigo = codigo.replace('\r\n', '\n').replace('\r', '\n')
    if len(codigo) > MAX_CARACTERES:
        resultado.avisar(Token('', '', 1, 1),
                         f'Entrada demasiado grande: máximo {MAX_CARACTERES} caracteres.')
        return [Token('FIN', '', 1, 1)]
    while i < len(codigo):
        c = codigo[i]
        if c in ' \t':
            i += 1
            columna += 1
            continue
        inicio, col = i, columna
        clase = 'SIMBOLO'
        detalle = ''
        if c == '\n':
            tokens.append(Token('SALTO', '\n', linea, columna))
            if len(tokens) > MAX_TOKENS:
                resultado.avisar(tokens[-1], f'Entrada demasiado grande: máximo {MAX_TOKENS} tokens.')
                return [Token('FIN', '', linea, columna)]
            i += 1
            linea += 1
            columna = 1
            continue
        # Comentarios # fuera de comillas; / siempre puede ser división.
        if c == '#':
            while i < len(codigo) and codigo[i] != '\n':
                i += 1
                columna += 1
            continue
        if codigo.startswith('/<', i):
            i += 2
            # Un nombre incorrecto se recoge completo sin comerse otra sentencia.
            while i < len(codigo) and codigo[i] not in '\n;,={}()':
                if codigo.startswith('>/', i):
                    i += 2
                    break
                i += 1
            clase = 'ID'
            if not IDENTIFICADOR.fullmatch(codigo[inicio:i]):
                clase = 'INVALIDO'
                detalle = 'Identificador inválido. Formato requerido: /<[a-zA-Z0-9]+>/.'
        elif c in '\"\'“‘':
            cierre = {'"': '"', "'": "'", '“': '”', '‘': '’'}[c]
            i += 1
            cerrado = False
            while i < len(codigo) and codigo[i] != '\n':
                if codigo[i] == cierre:
                    i += 1
                    cerrado = True
                    break
                if codigo[i] == '\\':
                    i += 1
                    if i >= len(codigo) or codigo[i] == '\n':
                        break
                i += 1
            clase = 'CADENA'
            if not cerrado:
                clase, detalle = 'INVALIDO', 'Literal sin comilla de cierre.'
        elif c.isdigit() or c == '.':
            i += 1
            # 12abc y 1.2.3 no deben convertirse en varios tokens válidos.
            while i < len(codigo) and (codigo[i].isalnum() or codigo[i] in '._'):
                i += 1
            valor = codigo[inicio:i]
            clase = 'REAL' if '.' in valor else 'ENTERO'
            if not NUMERO.fullmatch(valor):
                clase, detalle = 'INVALIDO', 'Número inválido; use 12 o 12.5, sin letras ni puntos adicionales.'
        elif c.isalpha() or c == '_':
            i += 1
            while i < len(codigo) and (codigo[i].isalnum() or codigo[i] == '_'):
                i += 1
            palabra = codigo[inicio:i]
            if palabra in TIPOS:
                clase = 'TIPO'
            elif palabra in {'while', 'void', 'return'}:
                clase = palabra.upper()
            else:
                clase = 'INVALIDO'
            if clase == 'INVALIDO':
                detalle = 'Palabra no admitida. Las variables usan /<nombre>/ y las funciones /<nombre>/().'
            if modo_pdf and clase == 'INVALIDO' and palabra.upper() not in ('AND', 'OR'):
                clase, detalle = ('TIPO' if palabra in ('int', 'float', 'String') else 'ID'), ''
        elif codigo[i:i + 2] in DOBLES:
            i += 2
        elif c in SIMPLES:
            i += 1
        else:
            i += 1
            clase, detalle = 'INVALIDO', 'Símbolo no admitido.'
        lexema = codigo[inicio:i]
        if modo_pdf and clase == 'TIPO':
            lexema = {'int': 'phi', 'float': 'rho', 'String': 'delta'}.get(lexema, lexema)
        if clase == 'INVALIDO' and lexema.upper() in ('AND', 'OR'):
            lexema = '&&' if lexema.upper() == 'AND' else '||'
            clase, detalle = 'SIMBOLO', ''
        token = Token(clase, lexema, linea, col)
        tokens.append(token)
        columna += i - inicio
        if detalle:
            resultado.avisar(token, detalle)
        if len(tokens) > MAX_TOKENS:
            resultado.avisar(token, f'Entrada demasiado grande: máximo {MAX_TOKENS} tokens.')
            return [Token('FIN', '', linea, columna)]
    tokens.append(Token('FIN', '', linea, columna))
    # Un mismo formato sirve para variables y funciones. Solo los paréntesis
    # que siguen al identificador lo convierten en nombre de función.
    i = 0
    while i < len(tokens) - 1:
        if tokens[i].clase == 'ID':
            j = i + 1
            while tokens[j].clase == 'SALTO':
                j += 1
            if tokens[j].lexema == '(':
                tokens[i].clase = 'NOMBRE'
        i += 1
    return tokens
