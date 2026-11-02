"""PDF III, páginas 5, 9, 11 y 26–33: uso antes de declaración."""
from reglas import INDEFINIDA


def revisar(tokens, simbolos, resultado):
    """Marca todas las apariciones; el símbolo indefinido permanece sin tipo."""
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.clase == 'ID' and simbolos.buscar(token.lexema) is None:
            simbolos.marcar_indefinida(token)
            resultado.error(token, INDEFINIDA)
        i += 1
