"""Casos de funciones del PDF III, adaptados a phi/rho/delta y /<variables>/."""
import random
import unittest
from analizador import analizar


def filas(r):
    return [(e['Lexema'], e['Renglón'], e['Descripción']) for e in r.errores]


class FuncionesPDF(unittest.TestCase):
    def test_funciones_validas_todos_tipos(self):
        r = analizar('''phi /<n>/;
rho /<r>/;
delta /<s>/;
phi /<Suma>/() { return 2 + 3; }
rho /<Media>/() { return /<Suma>/() / 2; }
delta /<Texto>/() { return "hola" + 'a'; }
void /<Proceso>/() { /<n>/ = /<Suma>/(); return; }
/<n>/ = /<Suma>/() * 3;
/<r>/ = /<Media>/();
/<s>/ = /<Texto>/();
/<Proceso>/();''')
        self.assertFalse(r.errores or r.observaciones, r)
        for nombre, tipo in [('/<Suma>/', 'phi'), ('/<Media>/', 'rho'), ('/<Texto>/', 'delta'), ('/<Proceso>/', 'void')]:
            self.assertIn({'Lexema': nombre, 'Tipo': tipo}, r.simbolos)

    def test_funcion_indefinida_pdf_III_13(self):
        r = analizar('phi /<Uno>/;\n/<Uno>/ = /<Otro>/();')
        self.assertEqual(filas(r), [('/<Otro>/', 2, 'Función indefinida')])
        self.assertIn({'Lexema': '/<Otro>/', 'Tipo': ''}, r.simbolos)
        self.assertFalse(r.observaciones)

    def test_retorno_incompatible_pdf_III_15(self):
        r = analizar('rho /<tres>/;\nphi /<Otro>/() {\nreturn /<tres>/ * 52;\n}')
        self.assertEqual(filas(r), [('/<tres>/', 3, 'Incompatibilidad de tipos, phi')])

    def test_prioridad_destino_indefinido_pdf_III_33(self):
        r = analizar('/<Otro>/ = 25.5 * /<C>/ / /<C2>/();')
        self.assertEqual(filas(r), [('/<Otro>/', 1, 'Variable indefinida'),
                                  ('/<C>/', 1, 'Variable indefinida'),
                                  ('/<C2>/', 1, 'Función indefinida')])

    def test_destino_conocido_indefinidas_y_tipos(self):
        r = analizar('phi /<n>/; /<n>/=/<Otro>/()+2.5/2;')
        self.assertEqual(filas(r), [('/<Otro>/', 1, 'Función indefinida'),
                                   ('2.5', 1, 'Incompatibilidad de tipos, phi'),
                                   ('/', 1, 'Incompatibilidad de tipos, phi')])

    def test_uso_antes_de_declaracion_no_se_borra(self):
        r = analizar('/<Suma>/();\nphi /<Suma>/() { return 1; }\n/<Suma>/();')
        self.assertEqual(filas(r), [('/<Suma>/', 1, 'Función indefinida')])
        self.assertIn({'Lexema': '/<Suma>/', 'Tipo': 'phi'}, r.simbolos)

    def test_llamada_como_instruccion(self):
        r = analizar('phi /<Uno>/(){return 1;} /<Uno>/(); void /<Dos>/(){} /<Dos>/();')
        self.assertFalse(r.errores or r.observaciones)

    def test_duplicada_conserva_primer_tipo(self):
        r = analizar('phi /<Suma>/(){return 1;}\nrho /<Suma>/(){return 2.5;}\n'
                     'phi /<n>/; /<n>/=/<Suma>/();')
        self.assertEqual(filas(r), [('/<Suma>/', 2, 'Declaración duplicada')])
        self.assertIn({'Lexema': '/<Suma>/', 'Tipo': 'phi'}, r.simbolos)
        self.assertFalse(r.observaciones)

    def test_llamada_incompatible(self):
        r = analizar('rho /<Media>/(){return 2.5;}\nphi /<n>/; /<n>/=/<Media>/();')
        self.assertEqual(filas(r), [('/<Media>/', 2, 'Incompatibilidad de tipos, phi')])

    def test_void_como_valor(self):
        r = analizar('void /<Mostrar>/(){}\nphi /<n>/; /<n>/=/<Mostrar>/()+1;')
        self.assertEqual(filas(r), [('/<Mostrar>/', 2, 'Incompatibilidad de tipos, phi')])

    def test_void_return(self):
        self.assertFalse(analizar('void /<A>/(){return;}').observaciones)
        r = analizar('void /<A>/(){return 1;}')
        self.assertTrue(r.observaciones)
        self.assertFalse(r.errores)

    def test_return_fuera_y_ausente(self):
        for codigo in ['return 1;', 'phi /<A>/(){}', 'rho /<A>/(){return;}', 'delta /<A>/(){return;}']:
            with self.subTest(codigo=codigo):
                self.assertTrue(analizar(codigo).observaciones)

    def test_return_comprueba_todos_operandos_y_operadores(self):
        r = analizar('phi /<A>/(){return /<x>/+2.5/2;}')
        self.assertEqual(filas(r), [('/<x>/', 1, 'Variable indefinida'),
                                  ('2.5', 1, 'Incompatibilidad de tipos, phi'),
                                  ('/', 1, 'Incompatibilidad de tipos, phi')])

    def test_return_otra_funcion(self):
        r = analizar('rho /<A>/(){return 1.5;} phi /<B>/(){return /<A>/();}')
        self.assertEqual(filas(r), [('/<A>/', 1, 'Incompatibilidad de tipos, phi')])

    def test_variables_locales_y_globales(self):
        r = analizar('phi /<g>/;\nvoid /<A>/(){rho /<g>/; /<g>/=1.5; phi /<local>/;}\n'
                     'void /<B>/(){/<local>/=1;}\n/<g>/=1.5;')
        self.assertEqual(filas(r), [('/<local>/', 3, 'Variable indefinida'),
                                  ('1.5', 4, 'Incompatibilidad de tipos, phi')])

    def test_duplicada_local(self):
        r = analizar('void /<A>/(){phi /<x>/; rho /<x>/;} void /<B>/(){rho /<x>/;}')
        self.assertEqual(filas(r), [('/<x>/', 1, 'Declaración duplicada')])

    def test_global_posterior_indefinida(self):
        r = analizar('void /<A>/(){/<x>/=1;} phi /<x>/;')
        self.assertEqual(filas(r), [('/<x>/', 1, 'Variable indefinida')])

    def test_while_en_funcion_y_return_anidado(self):
        r = analizar('phi /<Uno>/(){return 1;} phi /<A>/(){while(/<Uno>/()<2){return /<Uno>/();}}')
        self.assertFalse(r.errores or r.observaciones)

    def test_llamada_indefinida_condicion(self):
        r = analizar('while(/<Otro>/()<2){}')
        self.assertEqual(filas(r), [('/<Otro>/', 1, 'Función indefinida')])

    def test_void_no_vale_como_condicion(self):
        for condicion in ['/<A>/()', '/<A>/()==/<A>/()', '/<A>/()<1']:
            self.assertTrue(analizar('void /<A>/(){} while('+condicion+'){}').observaciones)

    def test_anidadas_no_publican_simbolos(self):
        r = analizar('phi /<A>/(){phi /<B>/(){return 1;} return 2;} /<B>/();')
        self.assertTrue(r.observaciones)
        self.assertEqual(filas(r), [('/<B>/', 1, 'Función indefinida')])

    def test_funcion_dentro_while_rechazada(self):
        r = analizar('while(1<2){void /<Oculta>/(){}} /<Oculta>/();')
        self.assertTrue(r.observaciones)
        self.assertEqual(filas(r), [('/<Oculta>/', 1, 'Función indefinida')])

    def test_recursiva_registrada_en_cabecera(self):
        r = analizar('phi /<A>/(){return /<A>/();}')
        self.assertFalse(r.errores or r.observaciones)

    def test_referencia_futura_en_funcion(self):
        r = analizar('phi /<A>/(){return /<B>/();} phi /<B>/(){return 1;}')
        self.assertEqual(filas(r), [('/<B>/', 1, 'Función indefinida')])

    def test_nombres_no_son_reservados_ni_variables(self):
        r = analizar('phi /<Suma>/; phi /<Suma>/(){return 1;} /<Suma>/=/<Suma>/();')
        self.assertFalse(r.errores or r.observaciones)
        r = analizar('phi /<Suma>/(){return 1;} /<suma>/();')
        self.assertEqual(filas(r), [('/<suma>/', 1, 'Función indefinida')])

    def test_espacios_y_saltos_cabecera(self):
        r = analizar('phi\n/<Suma>/\n(\n)\n{\nreturn 1;\n}\nphi /<n>/; /<n>/= /<Suma>/ (\n);')
        self.assertFalse(r.errores or r.observaciones, r)

    def test_rechazos_explicitos(self):
        for codigo in ['phi /<A>/(phi /<p>/){return 1;}', '/<A>/(1);', 'phi A(){return 1;}',
                       'void /<x>/;', 'phi A;', 'phi /<A>/()', 'phi /<A>/( {}', 'phi /<A>/){return 1;}',
                       'phi /<A_B>/(){return 1;}', 'phi /<Á>/(){return 1;}', 'phi 2A(){return 1;}',
                       'phi return(){return 1;}', '/<x>/=Suma;', '/<Suma>/()();']:
            with self.subTest(codigo=codigo):
                self.assertTrue(analizar(codigo).observaciones)

    def test_cabecera_invalida_no_contamina_entorno(self):
        r = analizar('phi /<A>/(1){phi /<x>/;} /<x>/=1; /<A>/();')
        self.assertTrue(r.observaciones)
        self.assertEqual(filas(r), [('/<x>/', 1, 'Variable indefinida'), ('/<A>/', 1, 'Función indefinida')])

    def test_reinicio_no_conserva_funciones(self):
        analizar('void /<A>/(){}')
        self.assertEqual(filas(analizar('/<A>/();')), [('/<A>/', 1, 'Función indefinida')])

    def test_entrada_aleatoria_con_funciones(self):
        rng = random.Random(4102026)
        partes = ['phi ', 'void ', 'return ', 'rho ', '/<A>/', '/<B>/', '/<Suma>/', '()', '(', ')', '{', '}',
                  '/<x>/', '1', '1.5', '"x"', ';', '\n', ',', '=', '+', 'while ', ' < ']
        for _ in range(2000):
            codigo = ''.join(rng.choices(partes, k=rng.randrange(1, 70)))
            r = analizar(codigo)
            self.assertIsInstance(r.errores, list)


if __name__ == '__main__':
    unittest.main()
