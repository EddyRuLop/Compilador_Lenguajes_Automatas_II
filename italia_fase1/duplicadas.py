"""PDF III, páginas 16–23: no redeclarar en el mismo ámbito."""
from reglas import DUPLICADA


def declarar(tokens, tipo, simbolos, resultado):
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if simbolos.duplicada(token.lexema):
            resultado.error(token, DUPLICADA)
            # Es esencial NO sobrescribir el tipo de la primera declaración.
        else:
            simbolos.declarar(token, tipo)
        i += 1
