"""Pruebas ejecutables: python -m unittest discover -s pruebas -v."""
import random
import unittest
from analizador import analizar
from pathlib import Path

# El ejemplo solo se carga cuando se ejecutan las pruebas manualmente.
EJEMPLO = (Path(__file__).parent / 'ejemplos' / '00_ejemplo_anterior.txt').read_text(encoding='utf-8')

BASE = '''phi /<a>/, /<b>/, /<c>/;
rho /<r>/, /<s>/, /<t>/;
delta /<m>/, /<n>/, /<o>/;
'''


def descripciones(resultado):
    return [e['Descripción'] for e in resultado.errores]


class ReglasPDF(unittest.TestCase):
    def test_ejemplo_valido(self):
        r = analizar(EJEMPLO)
        self.assertEqual(r.errores, [])
        self.assertEqual(r.observaciones, [])

    def test_pdf_II_pagina_13_lexemas_individuales(self):
        r = analizar('phi /<Uno>/, /<Dos>/;\nrho /<tres>/;\n'
                     '/<Uno>/ = 25.5 * /<tres>/ / 52;\n'
                     '/<Dos>/ = 10 + 52 - 3.14;\n/<tres>/ = "ejemplo";')
        self.assertEqual([(e['Lexema'], e['Renglón'], e['Descripción']) for e in r.errores],
                         [('25.5', 3, 'Incompatibilidad de tipos, phi'),
                          ('/<tres>/', 3, 'Incompatibilidad de tipos, phi'),
                          ('/', 3, 'Incompatibilidad de tipos, phi'),
                          ('3.14', 4, 'Incompatibilidad de tipos, phi'),
                          ('"ejemplo"', 5, 'Incompatibilidad de tipos, rho')])

    def test_todos_los_tipos_de_operandos(self):
        casos = [('phi', '1', True), ('phi', '1.5', False), ('phi', '"x"', False),
                 ('phi', "'x'", False), ('rho', '1', True), ('rho', '1.5', True),
                 ('rho', '"x"', False), ('rho', "'x'", False), ('delta', '1', False),
                 ('delta', '1.5', False), ('delta', '"x"', True), ('delta', "'x'", True)]
        for tipo, literal, correcto in casos:
            with self.subTest(tipo=tipo, literal=literal):
                r = analizar(f'{tipo} /<v>/; /<v>/ = {literal};')
                self.assertEqual(len(r.errores), 0 if correcto else 1)
                self.assertFalse(r.observaciones)

    def test_matriz_operadores(self):
        for tipo, operando, permitidos in [('phi', '2', '+-*'), ('rho', '2', '+-*/'),
                                            ('delta', '"x"', '+-')]:
            for op in '+-*/%':
                with self.subTest(tipo=tipo, op=op):
                    r = analizar(f'{tipo} /<v>/; /<v>/ = {operando} {op} {operando};')
                    self.assertEqual(len(r.errores), 0 if op in permitidos else 1)
                    if r.errores:
                        self.assertEqual(r.errores[0]['Lexema'], op)

    def test_indefinida_y_tipos_pdf_III_26(self):
        r = analizar(BASE + '/<a>/ = 25.5 * /<Otro>/ / 52;')
        self.assertEqual(descripciones(r), ['Variable indefinida',
                         'Incompatibilidad de tipos, phi', 'Incompatibilidad de tipos, phi'])

    def test_destino_indefinido_pdf_III_29_31(self):
        r = analizar(BASE + '/<Otro>/ = 25.5 * /<C>/ / "52";')
        self.assertEqual(descripciones(r), ['Variable indefinida'] * 2)
        self.assertEqual([e['Lexema'] for e in r.errores], ['/<Otro>/', '/<C>/'])
        self.assertIn({'Lexema': '/<Otro>/', 'Tipo': ''}, r.simbolos)

    def test_duplicadas_mismo_tipo_y_distinto_tipo(self):
        r = analizar('phi /<a>/, /<a>/; rho /<a>/; /<a>/ = 1.5;')
        self.assertEqual(descripciones(r), ['Declaración duplicada'] * 2 +
                         ['Incompatibilidad de tipos, phi'])
        self.assertIn({'Lexema': '/<a>/', 'Tipo': 'phi'}, r.simbolos)

    def test_uso_antes_de_declarar(self):
        r = analizar('/<x>/ = 5; phi /<x>/; /<x>/ = 1;')
        self.assertEqual(descripciones(r), ['Variable indefinida'])

    def test_renglones_y_reinicio(self):
        r = analizar('\nphi /<a>/;\n\n/<a>/=2.5;')
        self.assertEqual(r.errores[0]['Renglón'], 4)
        self.assertEqual(r.errores[0]['Token'], 'ErrSem1')
        otro = analizar('')
        self.assertFalse(otro.simbolos)
        self.assertEqual(len(r.errores), 1)

    def test_tabla_todos_los_lexemas(self):
        r = analizar('phi /<a>/; /<a>/ = 1 + 1;')
        self.assertEqual(r.simbolos, [{'Lexema': 'phi', 'Tipo': ''},
                         {'Lexema': '/<a>/', 'Tipo': 'phi'}, {'Lexema': ';', 'Tipo': ''},
                         {'Lexema': '=', 'Tipo': ''}, {'Lexema': '1', 'Tipo': 'phi'},
                         {'Lexema': '+', 'Tipo': ''}])

    def test_identificadores_mayusculas_digitos(self):
        r = analizar('phi /<123>/, /<A>/, /<a>/; /<123>/=1; /<A>/=2; /<a>/=3;')
        self.assertFalse(r.errores or r.observaciones)

    def test_caracteres_y_comillas_tipograficas(self):
        r = analizar('delta /<m>/; /<m>/ = “hola” - ‘x’;')
        self.assertFalse(r.errores or r.observaciones)

    def test_unarios_parentesis(self):
        r = analizar(BASE + '/<a>/ = -(2 + 3) * -4;\n/<r>/ = 1 / (2 + 3);')
        self.assertFalse(r.errores or r.observaciones)

    def test_inicializadores(self):
        r = analizar('rho /<a>/ = 3; phi /<b>/ = /<z>/ + 1.5;')
        self.assertEqual(descripciones(r), ['Variable indefinida', 'Incompatibilidad de tipos, phi'])

    def test_while_valido(self):
        r = analizar(BASE + 'while ((/<a>/ < 5 && /<r>/ >= 1.0) || !(2 == 3))\n{\n'
                     '/<a>/ = /<a>/ + 1;\n}')
        self.assertFalse(r.errores or r.observaciones)

    def test_while_indefinida(self):
        r = analizar('while (/<x>/ < 3) {}')
        self.assertEqual(descripciones(r), ['Variable indefinida'])
        self.assertFalse(r.observaciones)

    def test_ambitos(self):
        r = analizar('phi /<a>/; while (1<2) { rho /<a>/; /<a>/ = 1.5; '
                     'phi /<local>/; } /<a>/=1.5; /<local>/=1;')
        self.assertEqual(descripciones(r), ['Incompatibilidad de tipos, phi', 'Variable indefinida'])

    def test_while_infinito_no_se_ejecuta(self):
        r = analizar('while (1 == 1) { while (1 == 1) {} }')
        self.assertFalse(r.errores or r.observaciones)


class EntradasDificiles(unittest.TestCase):
    def test_lexemas_mal_formados(self):
        for literal in ['12abc', '1.2.3', '1e3', '.5', '1.', '１２', '1_000']:
            with self.subTest(literal=literal):
                r = analizar(f'phi /<a>/; /<a>/={literal};\n/<a>/=1.5;')
                self.assertTrue(r.observaciones)
                self.assertEqual(descripciones(r), ['Incompatibilidad de tipos, phi'])
        for nombre in ['/<a_b>/', '/<>/', '/<á>/', '/<a b>/', '[<a>]', '/a/']:
            r = analizar(f'phi {nombre};')
            self.assertTrue(r.observaciones, nombre)

    def test_sintaxis_no_se_acepta_silenciosamente(self):
        for codigo in ['phi;', 'phi /<a>/,;', 'phi /<a>/ /<b>/;', '/<a>/=;',
                       '/<a>/=1 2;', '/<a>/=1+;', '/<a>/=();', '/<a>/=(1;',
                       '/<a>/=1);', '/<a>/=f(1);', '/<a>/++;', 'while () {}',
                       'while (1<2)', 'while 1<2 {}', '}', 'while (1<2) {',
                       'if (1<2) {}', 'for (;;) {}', 'do {} while(1<2);',
                       'while (1) {}', 'while ("x" < 1) {}']:
            with self.subTest(codigo=codigo):
                self.assertTrue(analizar(codigo).observaciones)

    def test_no_declaracion_parcial(self):
        r = analizar('phi /<a>/, /<mal_nombre>/; /<a>/=1;')
        self.assertEqual(descripciones(r), ['Variable indefinida'])

    def test_literal_incompleto_y_recuperacion(self):
        r = analizar('delta /<m>/;\n/<m>/="sin cierre\nphi /<a>/; /<a>/=1.5;')
        self.assertTrue(r.observaciones)
        self.assertEqual(descripciones(r), ['Incompatibilidad de tipos, phi'])

    def test_texto_parecido_a_codigo_no_se_analiza(self):
        r = analizar('delta /<m>/; /<m>/ = "/<fantasma>/ ; while { = 3.4";')
        self.assertFalse(r.errores or r.observaciones)

    def test_sin_punto_y_coma_y_multilinea(self):
        r = analizar('phi /<a>/\n/<a>/ = (1 +\n2)\nwhile (/<a>/ <\n5)\n{\n/<a>/=2\n}')
        self.assertFalse(r.errores or r.observaciones)

    def test_comentarios_no_alteran_lineas(self):
        r = analizar('# comentario\nphi /<a>/; # comentario\n/<a>/=2.5;')
        self.assertEqual(r.errores[0]['Renglón'], 3)

    def test_anidacion_profunda_sin_recursion(self):
        r = analizar('phi /<a>/; /<a>/=' + '(' * 1500 + '1' + ')' * 1500 + ';')
        self.assertFalse(r.errores or r.observaciones)
        r = analizar('while(1<2){' * 1000 + '}' * 1000)
        self.assertFalse(r.errores or r.observaciones)

    def test_expresion_larga(self):
        r = analizar('phi /<a>/; /<a>/=' + '+'.join(['1'] * 7000) + ';')
        self.assertFalse(r.errores or r.observaciones)

    def test_numero_enorme_no_se_convierte_a_int(self):
        r = analizar('phi /<a>/; /<a>/=' + '9' * 10000 + ';')
        self.assertFalse(r.errores or r.observaciones)

    def test_limite_explicito(self):
        r = analizar('x' * 250001)
        self.assertTrue(r.observaciones)
        self.assertTrue(analizar('\n' * 50001).observaciones)

    def test_entradas_aleatorias_no_causan_excepcion(self):
        generador = random.Random(2026)
        piezas = ['phi ', 'rho ', 'delta ', '/<x>/', '/<y>/', '/<mal_>/', '1', '1.2',
                  '"x"', 'while', '(', ')', '{', '}', ';', ',', '=', '+', '/', '==',
                  '<', '&&', '!', '\n', ' ', '@']
        for _ in range(2000):
            codigo = ''.join(generador.choices(piezas, k=generador.randrange(1, 70)))
            r = analizar(codigo)
            self.assertIsInstance(r.errores, list)
            self.assertTrue(all(e['Descripción'] in {'Variable indefinida', 'Declaración duplicada',
                            'Incompatibilidad de tipos, phi', 'Incompatibilidad de tipos, rho',
                            'Incompatibilidad de tipos, delta'} for e in r.errores))


if __name__ == '__main__':
    unittest.main()
