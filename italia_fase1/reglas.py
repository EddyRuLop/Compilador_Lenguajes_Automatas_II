"""Reglas de tipos del PDF I (páginas 9–20), con los nombres del equipo."""
TIPOS = {'phi', 'rho', 'delta'}
INDEFINIDA = 'Variable indefinida'       # PDF III, tablas de páginas 9 y 11.
DUPLICADA = 'Declaración duplicada'      # PDF III, páginas 19, 21 y 23.
FUNCION_INDEFINIDA = 'Función indefinida'  # PDF III, páginas 13 y 33.
INCOMPATIBLE = 'Incompatibilidad de tipos, '

# Todo literal de texto, con comillas simples o dobles, tiene tipo delta.
TIPOS_ADMITIDOS = {
    'phi': {'phi'},
    'rho': {'phi', 'rho'},
    'delta': {'delta'},
}
OPERADORES_ADMITIDOS = {
    'phi': {'+', '-', '*'},
    'rho': {'+', '-', '*', '/'},
    'delta': {'+', '-'},
}
ARITMETICOS = {'+', '-', '*', '/', '%'}
RELACIONALES = {'<', '>', '<=', '>=', '==', '!='}
LOGICOS = {'&&', '||'}
TIPOS_LITERAL = {'ENTERO': 'phi', 'REAL': 'rho', 'CADENA': 'delta'}
