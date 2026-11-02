"""PDF I, páginas 9–14; PDF II, páginas 9 y 13: comprobar operadores.

La división siempre es incompatible con un destino phi, aunque 4/2 pudiera
ser exacto. El análisis comprueba reglas de tipos, no calcula los valores.
"""
from reglas import ARITMETICOS, OPERADORES_ADMITIDOS, INCOMPATIBLE


def revisar(tokens, tipo_destino, resultado):
    if tipo_destino is None:
        return
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.lexema in ARITMETICOS and token.lexema not in OPERADORES_ADMITIDOS[tipo_destino]:
            resultado.error(token, INCOMPATIBLE + tipo_destino)
        i += 1
