"""Separa instrucciones; una sentencia mal formada no bloquea las siguientes.

; o salto de línea terminan una instrucción. Dentro de paréntesis se permite
continuar en otra línea. while requiere (condición) y llaves, incluso vacío.
"""
from modelos import Instruccion
from expresiones import validar, reconocer_llamadas


def siguiente_visible(tokens, i):
    """Permite escribir una cabecera con saltos de línea entre sus partes."""
    while tokens[i].clase == 'SALTO':
        i += 1
    return i


def cabecera_funcion(tokens, i, resultado):
    """Acepta tipo /<Nombre>/() {. No consume la siguiente sentencia al fallar."""
    inicio = tokens[i]
    nombre_i = siguiente_visible(tokens, i + 1)
    nombre = tokens[nombre_i]
    j = siguiente_visible(tokens, nombre_i + 1)
    if tokens[j].lexema == '(':
        j = siguiente_visible(tokens, j + 1)
        if tokens[j].lexema == ')':
            j = siguiente_visible(tokens, j + 1)
            if tokens[j].lexema == '{':
                return Instruccion('FUNCION', nombre, [nombre], inicio.lexema), j + 1
    resultado.avisar(nombre, 'Declaración de función inválida. Use tipo /<Nombre>/() {; sin parámetros.')
    # Recoge una cabecera rota hasta un límite seguro. Su cuerpo se aísla para
    # que una declaración inválida no publique variables o funciones globales.
    j = nombre_i + 1
    while tokens[j].clase not in {'FIN', 'SALTO'} and tokens[j].lexema not in {'{', '}', ';'}:
        j += 1
    if tokens[j].lexema == '{':
        return Instruccion('BLOQUE_INVALIDO', inicio), j + 1
    return None, j


def separar(tokens, resultado):
    instrucciones, bloques = [], []
    i = 0
    while tokens[i].clase != 'FIN':
        t = tokens[i]
        if t.clase == 'SALTO' or t.lexema == ';':
            i += 1
            continue
        if t.lexema == '}':
            if bloques:
                bloques.pop()
                instrucciones.append(Instruccion('CIERRE', t))
            else:
                resultado.avisar(t, 'Llave de cierre sin bloque correspondiente.')
            i += 1
            continue
        if t.clase in {'TIPO', 'VOID'}:
            nombre_i = siguiente_visible(tokens, i + 1)
            if tokens[nombre_i].clase == 'NOMBRE':
                inst, i = cabecera_funcion(tokens, i, resultado)
                if inst:
                    if bloques and inst.clase == 'FUNCION':
                        resultado.avisar(inst.inicio, 'Las funciones solo se declaran en el ámbito global.')
                        inst.clase = 'BLOQUE_INVALIDO'
                    bloques.append(inst.inicio)
                    instrucciones.append(inst)
                continue
        if t.clase == 'WHILE':
            i += 1
            while tokens[i].clase == 'SALTO':
                i += 1
            if tokens[i].lexema != '(':
                resultado.avisar(t, 'while necesita una condición entre paréntesis.')
                continue
            i += 1
            profundidad = 1
            expresion = []
            while tokens[i].clase != 'FIN' and profundidad:
                actual = tokens[i]
                if actual.lexema in {'{', '}', ';'}:
                    break
                if actual.lexema == '(':
                    profundidad += 1
                elif actual.lexema == ')':
                    profundidad -= 1
                    if profundidad == 0:
                        i += 1
                        break
                if actual.clase != 'SALTO':
                    expresion.append(actual)
                i += 1
            if profundidad:
                resultado.avisar(t, 'Falta cerrar el paréntesis de while.')
            expresion = reconocer_llamadas(expresion, resultado) if expresion else []
            postfija = validar(expresion, resultado, condicion=True) if expresion else None
            if not expresion:
                resultado.avisar(t, 'while no puede tener una condición vacía.')
            while tokens[i].clase == 'SALTO':
                i += 1
            if tokens[i].lexema == '{':
                # Incluso si la cabecera está mal, conserva las llaves y revisa
                # las instrucciones completas del interior sin ejecutar el ciclo.
                bloques.append(t)
                instrucciones.append(Instruccion('WHILE', t, expresion=expresion or [],
                                                   postfija=postfija or []))
                i += 1
            else:
                resultado.avisar(t, 'Falta { después de la condición de while.')
            continue
        if t.lexema == '{':
            resultado.avisar(t, 'Se esperaba una cabecera de while o de función antes de {.')
            # Bloque de recuperación: mantiene el equilibrio sin crear un while.
            bloques.append(t)
            instrucciones.append(Instruccion('BLOQUE_INVALIDO', t))
            i += 1
            continue
        parte = []
        profundidad = 0
        while tokens[i].clase != 'FIN' and tokens[i].lexema not in {';', '{', '}'}:
            actual = tokens[i]
            if actual.clase == 'SALTO':
                if profundidad == 0:
                    break
                # Si la siguiente línea parece iniciar otra sentencia, se
                # recupera aquí aun cuando haya quedado abierto un paréntesis.
                siguiente = tokens[i + 1]
                if siguiente.clase in {'TIPO', 'VOID', 'RETURN', 'WHILE'} or (
                    siguiente.clase == 'ID' and tokens[i + 2].lexema == '='):
                    break
            else:
                parte.append(actual)
                if actual.lexema == '(':
                    profundidad += 1
                elif actual.lexema == ')':
                    profundidad = max(0, profundidad - 1)
            i += 1
        if parte:
            instruccion = construir(parte, resultado)
            if instruccion:
                instrucciones.append(instruccion)
    while bloques:
        apertura = bloques.pop()
        resultado.avisar(apertura, 'Falta } para cerrar el bloque.')
        instrucciones.append(Instruccion('CIERRE', apertura))
    return instrucciones


def construir(parte, resultado):
    """No crea declaraciones parciales a partir de una lista mal escrita."""
    inicio = parte[0]
    i = 0
    while i < len(parte):
        if parte[i].clase == 'INVALIDO':
            return None
        i += 1
    if inicio.clase == 'RETURN':
        expresion = reconocer_llamadas(parte[1:], resultado)
        if expresion is None:
            return None
        postfija = validar(expresion, resultado) if expresion else []
        if postfija is not None:
            return Instruccion('RETURN', inicio, expresion=expresion, postfija=postfija)
        return None
    if inicio.clase == 'NOMBRE':
        expresion = reconocer_llamadas(parte, resultado)
        if expresion is not None:
            if len(expresion) == 1 and expresion[0].clase == 'LLAMADA':
                return Instruccion('LLAMADA', inicio, expresion=expresion)
            resultado.avisar(inicio, 'Una llamada como instrucción debe ser /<Nombre>/().')
        return None
    if inicio.clase == 'VOID':
        resultado.avisar(inicio, 'void solo declara funciones: void /<Nombre>/() { ... }.')
        return None
    if inicio.clase == 'TIPO':
        nombres, i = [], 1
        while i < len(parte):
            if parte[i].clase != 'ID':
                resultado.avisar(parte[i], 'Se esperaba un identificador después del tipo o de la coma.')
                return None
            nombres.append(parte[i])
            i += 1
            if i == len(parte) or parte[i].lexema == '=':
                break
            if parte[i].lexema != ',':
                resultado.avisar(parte[i], 'Se esperaba una coma entre identificadores.')
                return None
            i += 1
            if i == len(parte):
                resultado.avisar(parte[-1], 'Falta un identificador después de la coma.')
                return None
        if not nombres:
            resultado.avisar(inicio, 'La declaración necesita al menos un identificador.')
            return None
        expresion, postfija = [], []
        if i < len(parte):
            expresion = reconocer_llamadas(parte[i + 1:], resultado)
            if expresion is None:
                return None
            if not expresion:
                resultado.avisar(parte[i], 'Falta la expresión después de =.')
                return None
            postfija = validar(expresion, resultado)
            if postfija is None:
                return None
        return Instruccion('DECLARACION', inicio, nombres, inicio.lexema, expresion, postfija)
    if inicio.clase == 'ID' and len(parte) >= 2 and parte[1].lexema == '=':
        expresion = reconocer_llamadas(parte[2:], resultado)
        if expresion is None:
            return None
        if not expresion:
            resultado.avisar(parte[1], 'Falta la expresión después de =.')
            return None
        postfija = validar(expresion, resultado)
        if postfija is not None:
            return Instruccion('ASIGNACION', inicio, [inicio], expresion=expresion, postfija=postfija)
        return None
    resultado.avisar(inicio, 'Instrucción no admitida: use declaración, asignación, llamada, return o while. '
                      'Para incrementar use /<x>/ = /<x>/ + 1.')
    return None
