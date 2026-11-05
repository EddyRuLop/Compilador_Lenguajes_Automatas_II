"""Funciones con parámetros tipados y reglas de retorno del PDF III.

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
        simbolos.parametros[nombre] = inst.parametros
        simbolos.filas_funciones[nombre]['Tipo'] = inst.tipo
    # Contexto del cuerpo: tipo escrito y presencia de un return con valor.
    return {'inicio': inst.inicio, 'tipo': inst.tipo, 'retorno': False}


def revisar_llamadas(tokens, simbolos, resultado):
    """El error conserva /<Suma>/; los paréntesis no son parte del lexema."""
    pendientes = list(reversed(tokens))
    while pendientes:
        t = pendientes.pop()
        if t.clase != 'LLAMADA':
            continue
        if t.lexema not in simbolos.funciones:
            resultado.error(t, FUNCION_INDEFINIDA)
            formales = []
        else:
            formales = simbolos.parametros[t.lexema]
            if len(t.argumentos) != len(formales):
                resultado.avisar(t, f'La función {t.lexema} espera {len(formales)} argumentos '
                                   f'y recibió {len(t.argumentos)}.')
        for indice, argumento in enumerate(t.argumentos):
            indefinidas.revisar(argumento, simbolos, resultado)
            if indice < len(formales):
                tipo = formales[indice][1]
                asignaciones.revisar(argumento, tipo, simbolos, resultado)
                aritmetica.revisar(argumento, tipo, resultado)
        for argumento in reversed(t.argumentos):
            pendientes.extend(reversed(argumento))


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
