"""Funciones sin parámetros y reglas del PDF III (páginas 6, 7, 13, 15 y 33).

/<Suma>/ es un nombre elegido por el usuario; void es un tipo de retorno.
Las funciones se registran al encontrar su cabecera, antes de revisar el cuerpo.
"""
from reglas import FUNCION_INDEFINIDA, DUPLICADA
import indefinidas
import asignaciones
import aritmetica


def declarar(inst, simbolos, resultado):
    """Conserva la primera firma; una llamada previa no cuenta como declaración."""
    nombre = inst.inicio.lexema
    if nombre in simbolos.funciones:
        resultado.error(inst.inicio, DUPLICADA)
    else:
        simbolos.funciones[nombre] = inst.tipo
        simbolos.filas_funciones[nombre]['Tipo'] = inst.tipo
    # Contexto del cuerpo: tipo escrito y presencia de un return con valor.
    return {'inicio': inst.inicio, 'tipo': inst.tipo, 'retorno': False}


def revisar_llamadas(tokens, simbolos, resultado):
    """El error conserva /<Suma>/; los paréntesis no son parte del lexema."""
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t.clase == 'LLAMADA' and t.lexema not in simbolos.funciones:
            resultado.error(t, FUNCION_INDEFINIDA)
        i += 1


def revisar_retorno(inst, contexto, simbolos, resultado):
    if contexto is None:
        resultado.avisar(inst.inicio, 'return solo se permite dentro de una función.')
        return
    tipo = contexto['tipo']
    indefinidas.revisar(inst.expresion, simbolos, resultado)
    revisar_llamadas(inst.expresion, simbolos, resultado)
    if tipo == 'void':
        if inst.expresion:
            resultado.avisar(inst.inicio, 'Una función void solo admite return sin valor.')
        return
    if not inst.expresion:
        resultado.avisar(inst.inicio, f'La función {contexto["inicio"].lexema} requiere return con valor de tipo {tipo}.')
        return
    contexto['retorno'] = True
    # Se usan las mismas reglas que para una asignación al tipo de la función.
    # Ejemplo PDF III p. 15: phi /<Otro>/() { return /<real>/ * 52; }.
    asignaciones.revisar(inst.expresion, tipo, simbolos, resultado)
    aritmetica.revisar(inst.expresion, tipo, resultado)


def cerrar(contexto, resultado):
    """Solo exige presencia de return: no analiza todos los caminos de ejecución."""
    if contexto['tipo'] != 'void' and not contexto['retorno']:
        resultado.avisar(contexto['inicio'], 'Falta al menos un return con valor en esta función.')
