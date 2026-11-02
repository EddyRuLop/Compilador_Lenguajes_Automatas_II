"""Coordinador de las capas. Cada llamada crea un estado limpio e independiente."""
from modelos import Resultado
from entrada import tokenizar
from sintaxis import separar
from simbolos import Simbolos
import indefinidas
import duplicadas
import asignaciones
import aritmetica
import ciclos
import funciones


def analizar(codigo):
    resultado = Resultado()
    tokens = tokenizar(codigo, resultado)
    instrucciones = separar(tokens, resultado)
    simbolos = Simbolos(tokens, resultado)
    bloques = []
    contexto = None
    omitir = 0
    i = 0
    while i < len(instrucciones):
        inst = instrucciones[i]
        # Un bloque rechazado (por ejemplo, una función anidada) no publica
        # declaraciones ni modifica el contexto de la función exterior.
        if omitir:
            if inst.clase in {'FUNCION', 'WHILE', 'BLOQUE_INVALIDO'}:
                omitir += 1
            elif inst.clase == 'CIERRE':
                omitir -= 1
            i += 1
            continue
        if inst.clase == 'BLOQUE_INVALIDO':
            omitir = 1
            i += 1
            continue
        if inst.clase == 'DECLARACION':
            # El inicializador usa el entorno anterior; x=x no declara primero x.
            if inst.expresion:
                indefinidas.revisar(inst.expresion, simbolos, resultado)
                funciones.revisar_llamadas(inst.expresion, simbolos, resultado)
                asignaciones.revisar(inst.expresion, inst.tipo, simbolos, resultado)
                aritmetica.revisar(inst.expresion, inst.tipo, resultado)
            duplicadas.declarar(inst.nombres, inst.tipo, simbolos, resultado)
        elif inst.clase == 'ASIGNACION':
            indefinidas.revisar(inst.nombres + inst.expresion, simbolos, resultado)
            funciones.revisar_llamadas(inst.expresion, simbolos, resultado)
            destino = simbolos.buscar(inst.inicio.lexema)
            # Si no hay tipo de destino, ambas capas siguientes se abstienen.
            asignaciones.revisar(inst.expresion, destino, simbolos, resultado)
            aritmetica.revisar(inst.expresion, destino, resultado)
        elif inst.clase == 'WHILE':
            if inst.postfija:
                indefinidas.revisar(inst.expresion, simbolos, resultado)
                funciones.revisar_llamadas(inst.expresion, simbolos, resultado)
                ciclos.revisar(inst.postfija, simbolos, resultado)
            simbolos.entrar()
            bloques.append('WHILE')
        elif inst.clase == 'FUNCION':
            contexto = funciones.declarar(inst, simbolos, resultado)
            simbolos.entrar()
            bloques.append('FUNCION')
        elif inst.clase == 'RETURN':
            funciones.revisar_retorno(inst, contexto, simbolos, resultado)
        elif inst.clase == 'LLAMADA':
            funciones.revisar_llamadas(inst.expresion, simbolos, resultado)
        elif inst.clase == 'CIERRE':
            simbolos.salir()
            if bloques and bloques.pop() == 'FUNCION':
                funciones.cerrar(contexto, resultado)
                contexto = None
        i += 1
    return resultado
