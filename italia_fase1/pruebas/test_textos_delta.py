"""Todos los literales de texto tienen tipo delta."""
import unittest
from analizador import analizar
from entrada import tokenizar
from modelos import Resultado


class TextosDelta(unittest.TestCase):
    def test_comillas_y_longitudes(self):
        literales = ["'A'", "'Hola'", "''", '"A"', '"Hola"', '""',
                     '‘A’', '‘Hola’', '‘’', '“Hola”', '“”', r"'a\'b'"]
        i = 0
        while i < len(literales):
            literal = literales[i]
            r = analizar('delta /<texto>/; /<texto>/=' + literal + ';')
            self.assertFalse(r.errores or r.observaciones, literal)
            self.assertIn({'Lexema': literal, 'Tipo': 'delta'}, r.simbolos)
            i += 1

    def test_misma_categoria_lexica(self):
        r = Resultado()
        tokens = tokenizar("'A' \"A\" ‘A’ “A”", r)
        i = 0
        while i < len(tokens) - 1:
            self.assertEqual(tokens[i].clase, 'CADENA')
            i += 1

    def test_funciones_operaciones_y_while(self):
        r = analizar('delta /<Texto>/(){return \'Hola\' + " mundo";} '
                     'delta /<t>/; /<t>/=/<Texto>/()-\'o\'; '
                     'while (/<t>/ != \'\') { /<t>/=""; }')
        self.assertFalse(r.errores or r.observaciones, r)

    def test_texto_no_es_numero(self):
        r = analizar('phi /<n>/; rho /<r>/; /<n>/=\'5\'; /<r>/=\'2.5\';')
        self.assertFalse(r.observaciones)
        self.assertEqual(len(r.errores), 2)
        self.assertEqual(r.errores[0]['Descripción'], 'Incompatibilidad de tipos, phi')
        self.assertEqual(r.errores[1]['Descripción'], 'Incompatibilidad de tipos, rho')

    def test_comillas_incompletas_siguen_siendo_error(self):
        r = analizar("delta /<t>/; /<t>/='sin cierre\n/<t>/='bien';")
        self.assertTrue(r.observaciones)
        self.assertFalse(r.errores)
        self.assertIn({'Lexema': "'bien'", 'Tipo': 'delta'}, r.simbolos)


if __name__ == '__main__':
    unittest.main()
