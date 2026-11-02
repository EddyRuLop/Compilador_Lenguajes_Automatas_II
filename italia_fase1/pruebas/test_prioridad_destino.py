"""Prioridad de variable destino indefinida: PDF III, página 29."""
import unittest
from analizador import analizar


class PrioridadDestino(unittest.TestCase):
    def errores(self, codigo):
        resultado = analizar(codigo)
        self.assertFalse(resultado.observaciones)
        return [(e['Lexema'], e['Renglón'], e['Descripción'])
                for e in resultado.errores]

    def test_ejemplo_diapositiva(self):
        self.assertEqual(self.errores(
            'phi /<Uno>/, /<Dos>/;\ndelta /<tres>/;\n'
            '/<Otro>/ = 25.5 * /<Uno>/ / "52";\n'
            '/<Dos>/ = 10 + 52 - 3;\n/<tres>/ = "ejemplo";'),
            [('/<Otro>/', 3, 'Variable indefinida')])

    def test_omite_indefinidas_y_llamadas_de_la_expresion(self):
        self.assertEqual(self.errores(
            '/<Otro>/ = /<desconocida>/ + /<Funcion>/();'),
            [('/<Otro>/', 1, 'Variable indefinida')])

    def test_continua_con_instrucciones_siguientes(self):
        self.assertEqual(self.errores(
            'phi /<n>/;\n/<Otro>/ = /<desconocida>/ + /<Funcion>/();\n'
            '/<n>/ = "texto";\n/<n>/ = /<otra>/;'),
            [('/<Otro>/', 2, 'Variable indefinida'),
             ('"texto"', 3, 'Incompatibilidad de tipos, phi'),
             ('/<otra>/', 4, 'Variable indefinida')])

    def test_destino_declarado_conserva_errores_de_expresion(self):
        self.assertEqual(self.errores(
            'phi /<n>/;\n/<n>/ = /<desconocida>/ + /<Funcion>/();'),
            [('/<desconocida>/', 2, 'Variable indefinida'),
             ('/<Funcion>/', 2, 'Función indefinida')])


if __name__ == '__main__':
    unittest.main()
