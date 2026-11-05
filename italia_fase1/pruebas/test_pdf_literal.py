import unittest

from analizador import analizar
from fase2_triplos import generar_triplos


class EjemplosLiteralesPDF(unittest.TestCase):
    def test_while_con_y_sin_operador_logico(self):
        for condicion, ramas in [
            ('x<100', ['_ TRUE 5', '_ FALSE 12']),
            ('x<100 || x < 200', ['_ TRUE 9', '_ FALSE 5', 'T1 x =',
                                 'T1 200 <', '_ TRUE 9', '_ FALSE 16']),
            ('x<100 && x < 200', ['_ TRUE 5', '_ FALSE 16', 'T1 x =',
                                 'T1 200 <', '_ TRUE 9', '_ FALSE 16']),
        ]:
            with self.subTest(condicion=condicion):
                codigo = f'while ({condicion})\n{{\n b= x-2;\n x=x+1;\n}}'
                esperados = ['T1 x =', 'T1 100 <'] + ramas + [
                    'T1 x =', 'T1 2 -', 'b T1 =', 'T1 x =', 'T1 1 +',
                    'x T1 =', '_ 1 JMP']
                self.comparar(codigo, esperados)
                errores = analizar(codigo, modo_pdf=True).errores
                self.assertCountEqual([(e['Lexema'], e['Descripción']) for e in errores],
                                      [('x', 'Variable indefinida'), ('b', 'Variable indefinida')])

    def test_funciones_de_cero_uno_y_dos_parametros(self):
        for params, args, valor, paso in [
            ('', '', 'r3', []),
            ('int a', '75', 'r3', ['T1 75 =', 'a T1 =']),
            ('int a , float w', '75 , 1.15', 'w',
             ['T1 75 =', 'a T1 =', 'T1 1.15 =', 'w T1 =']),
        ]:
            with self.subTest(params=params):
                codigo = f"""r2 = 100;
i1 = 35 * r2 ;
float suma ({params})
{{
  r3 = a + r2 ;
  r1 = {valor} + 2.6 ;
  return r1 ;
}}
i2 = i2 % 2 ;
i3 = suma ( {args} ) ;"""
                esperados = ['T1 100 =', 'r2 T1 =', 'T1 35 =', 'T1 r2 *',
                             'i1 T1 =', '_ 14 JMP', 'T1 a =', 'T1 r2 +',
                             'r3 T1 =', f'T1 {valor} =', 'T1 2.6 +', 'r1 T1 =',
                             f'_ {18 + len(paso)} JMP', 'T1 i2 =', 'T1 2 %',
                             'i2 T1 ='] + paso + ['_ 7 JMP', 'T1 r1 =', 'i3 T1 =']
                self.comparar(codigo, esperados)

    def test_destino_indefinido_pdf_iii(self):
        codigo = '''int Uno, Dos
String tres
Otro = 25.5 * Uno / “52” ;
Dos = 10 + 52 -3 ;
tres = “ejemplo” ;'''
        errores = analizar(codigo, modo_pdf=True).errores
        self.assertEqual([(e['Lexema'], e['Renglón'], e['Descripción']) for e in errores],
                         [('Otro', 3, 'Variable indefinida')])
        self.assertTrue(generar_triplos(codigo, modo_pdf=True))

    def comparar(self, codigo, esperados):
        filas = generar_triplos(codigo, modo_pdf=True)
        self.assertEqual(filas, [(n, *('' if c == '_' else c for c in fila.split()))
                                 for n, fila in enumerate(esperados, 1)])
