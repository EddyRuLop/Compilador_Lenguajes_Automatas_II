"""PDF I, páginas 15–20: comprobar operandos contra el tipo del destino."""
from reglas import TIPOS_ADMITIDOS, INCOMPATIBLE, TIPOS_LITERAL


def revisar(tokens, tipo_destino, simbolos, resultado):
    if tipo_destino is None:
        return  # Prioridad del PDF III, página 29.
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.clase in {'ID', 'LLAMADA'} or token.clase in TIPOS_LITERAL:
            tipo = simbolos.tipo(token)
            # Una indefinida ya tiene su propio error. No inventar su tipo.
            if tipo is not None and tipo not in TIPOS_ADMITIDOS[tipo_destino]:
                resultado.error(token, INCOMPATIBLE + tipo_destino)
        i += 1
