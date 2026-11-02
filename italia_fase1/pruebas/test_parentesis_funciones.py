"""Variables y funciones comparten formato; () distingue las funciones."""
import unittest
from analizador import analizar


class FuncionesConDelimitadores(unittest.TestCase):
    def test_homonimos_con_tipos_distintos_en_ambos_ordenes(self):
        casos = ['rho /<dato>/; phi /<dato>/(){return 1;}',
                 'phi /<dato>/(){return 1;} rho /<dato>/;']
        i = 0
        while i < len(casos):
            r = analizar(casos[i] + '/<dato>/=1.5; phi /<n>/; /<n>/=/<dato>/();')
            self.assertFalse(r.errores or r.observaciones, r)
            self.assertIn({'Lexema': '/<dato>/', 'Tipo': 'rho'}, r.simbolos)
            self.assertIn({'Lexema': '/<dato>/', 'Tipo': 'phi'}, r.simbolos)
            i += 1

    def test_funcion_no_declara_variable_homonima(self):
        r = analizar('phi /<dato>/(){return 1;} /<dato>/=2;')
        self.assertEqual(len(r.errores), 1)
        self.assertEqual(r.errores[0]['Descripción'], 'Variable indefinida')
        self.assertIn({'Lexema': '/<dato>/', 'Tipo': ''}, r.simbolos)
        self.assertIn({'Lexema': '/<dato>/', 'Tipo': 'phi'}, r.simbolos)

    def test_variable_no_declara_funcion_homonima(self):
        r = analizar('rho /<dato>/; /<dato>/();')
        self.assertEqual(len(r.errores), 1)
        self.assertEqual(r.errores[0]['Descripción'], 'Función indefinida')
        self.assertIn({'Lexema': '/<dato>/', 'Tipo': 'rho'}, r.simbolos)
        self.assertIn({'Lexema': '/<dato>/', 'Tipo': ''}, r.simbolos)

    def test_misma_expresion_regular_incluye_digitos(self):
        r = analizar('phi /<123>/(){return 1;} phi /<123>/; /<123>/=/<123>/();')
        self.assertFalse(r.errores or r.observaciones, r)

    def test_espacios_comentarios_y_saltos(self):
        r = analizar('phi /<Suma>/ # cabecera\n (\n)\n{ return 2 + 3; }\n'
                     'void /<Proceso>/ () { /<Suma>/ (); }\n'
                     'phi /<n>/; /<n>/ = /<Suma>/ (\n);\n'
                     'while (/<Suma>/ () < 10) { /<Proceso>/ (); }')
        self.assertFalse(r.errores or r.observaciones, r)

    def test_sintaxis_antigua_rechazada_y_sin_parentesis_es_variable(self):
        casos = ['phi Suma(){return 1;}', 'Suma();',
                 'phi /<n>/; /<n>/=Suma();', 'void /<Suma>/;']
        i = 0
        while i < len(casos):
            self.assertTrue(analizar(casos[i]).observaciones, casos[i])
            i += 1
        r = analizar('phi /<Suma>/; /<Suma>/=3;')
        self.assertFalse(r.errores or r.observaciones)

    def test_contenido_de_cadena_no_se_convierte_en_funcion(self):
        r = analizar('delta /<texto>/; /<texto>/="/<NoExiste>/()";')
        self.assertFalse(r.errores or r.observaciones)
        self.assertNotIn({'Lexema': '/<NoExiste>/', 'Tipo': ''}, r.simbolos)


if __name__ == '__main__':
    unittest.main()
