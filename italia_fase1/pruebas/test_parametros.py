"""Regresión: analizar y generar triplos admiten funciones con argumentos."""
import unittest

from analizador import analizar
from fase2_triplos import generar_triplos


class Parametros(unittest.TestCase):
    def test_cuerpo_con_parametros_locales_asignaciones_y_while(self):
        codigo = '''phi /<base>/ = 10;
phi /<Suma>/(phi /<a>/, phi /<b>/)
{
    phi /<resultado>/ = /<a>/ + /<b>/;
    while (/<resultado>/ < /<base>/) {
        /<resultado>/ = /<resultado>/ + 1;
    }
    return /<resultado>/;
}
phi /<total>/ = /<Suma>/(2, 3);
'''
        r = analizar(codigo)
        self.assertFalse(r.errores or r.observaciones, r)
        avisos = []
        triplos = generar_triplos(codigo, avisos=avisos)
        self.assertTrue(triplos)
        self.assertFalse(avisos)
        self.assertTrue(any(objeto == '/<a>/' and op == '='
                            for _, objeto, _, op in triplos))

    def test_llamadas_anidadas_y_expresiones_en_argumentos(self):
        r = analizar('''phi /<Id>/(phi /<x>/) { return /<x>/; }
phi /<Suma>/(phi /<a>/, phi /<b>/) { return /<a>/ + /<b>/; }
phi /<n>/ = /<Suma>/((1 + 2) * 3, /<Id>/( /<Suma>/(4, 5) ));
while (/<Id>/(1) < /<Suma>/(2, 3)) { /<Id>/(2); }
''')
        self.assertFalse(r.errores or r.observaciones, r)

    def test_tipos_de_parametros(self):
        r = analizar('''delta /<Texto>/(delta /<s>/, rho /<r>/) { return /<s>/; }
delta /<texto>/ = /<Texto>/("hola", 1.5);
/<Texto>/(2, "mal");''')
        self.assertFalse(r.observaciones, r)
        self.assertEqual([(e['Lexema'], e['Descripción']) for e in r.errores],
                         [('2', 'Incompatibilidad de tipos, delta'),
                          ('"mal"', 'Incompatibilidad de tipos, rho')])

    def test_cantidad_de_argumentos(self):
        for argumentos in ['', '1, 2']:
            with self.subTest(argumentos=argumentos):
                r = analizar('phi /<Id>/(phi /<x>/){return /<x>/;} '
                             f'/<Id>/({argumentos});')
                self.assertFalse(r.errores)
                self.assertEqual(len(r.observaciones), 1)
                self.assertIn('espera 1 argumentos', r.observaciones[0])

    def test_parametros_no_salen_del_ambito(self):
        r = analizar('phi /<Id>/(phi /<x>/){return /<x>/;} /<x>/=1;')
        self.assertEqual([e['Descripción'] for e in r.errores], ['Variable indefinida'])
        self.assertFalse(r.observaciones)

    def test_parametro_duplicado(self):
        r = analizar('phi /<Id>/(phi /<x>/, rho /<x>/){return /<x>/;}')
        self.assertEqual([e['Descripción'] for e in r.errores], ['Declaración duplicada'])
        self.assertFalse(r.observaciones)

    def test_parametro_oculta_global_y_se_restaura_al_salir(self):
        r = analizar('rho /<x>/; phi /<Id>/(phi /<x>/){return /<x>/;} /<x>/=1.5;')
        self.assertFalse(r.errores or r.observaciones, r)

    def test_indefinidas_dentro_de_argumentos(self):
        r = analizar('phi /<Id>/(phi /<x>/){return /<x>/;} /<Id>/( /<Otra>/( /<z>/ ) );')
        self.assertCountEqual([(e['Lexema'], e['Descripción']) for e in r.errores],
                              [('/<Otra>/', 'Función indefinida'), ('/<z>/', 'Variable indefinida')])
        self.assertFalse(r.observaciones)

    def test_recursiva_con_parametros(self):
        r = analizar('phi /<Id>/(phi /<x>/){return /<Id>/( /<x>/ - 1 );}')
        self.assertFalse(r.errores or r.observaciones, r)

    def test_cabeceras_invalidas_no_publican_el_cuerpo(self):
        for params in ['phi', 'phi /<p>/,', '/<p>/', 'void /<p>/', 'phi /<p>/ rho /<q>/']:
            with self.subTest(params=params):
                r = analizar(f'phi /<Id>/({params}) {{ phi /<local>/; }} /<local>/=1;')
                self.assertTrue(r.observaciones)
                self.assertEqual([e['Descripción'] for e in r.errores], ['Variable indefinida'])

    def test_argumentos_invalidos_se_recuperan(self):
        for args in [',1', '1,', '1,,2', '1 +', '(1,2)', '1 2']:
            with self.subTest(args=args):
                r = analizar(f'void /<Id>/(phi /<x>/){{}} /<Id>/({args}); phi /<ok>/; /<ok>/=1;')
                self.assertTrue(r.observaciones)
                self.assertFalse(r.errores, r)


if __name__ == '__main__':
    unittest.main()
