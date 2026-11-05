import csv
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from analizador import analizar
from fase2_triplos import generar_triplos, guardar_txt


class FaseDos(unittest.TestCase):
    def test_funcion_dos_parametros_tabla_del_apunte(self):
        filas = generar_triplos("""
            /<r2>/ = 100; /<i1>/ = 35 * /<r2>/;
            rho /<suma>/(phi /<a>/, rho /<w>/) {
                /<r3>/ = /<a>/ + /<r2>/;
                /<r1>/ = /<w>/ + 2.6;
                return /<r1>/;
            }
            /<i2>/ = /<i2>/ % 2;
            /<i3>/ = /<suma>/(75, 1.15);
        """)
        self.assertEqual(len(filas), 23)
        self.assertEqual([fila for fila in filas if fila[-1] == 'JMP'],
                         [(6, '', '14', 'JMP'), (13, '', '22', 'JMP'),
                          (21, '', '7', 'JMP')])
        self.assertEqual(filas[-2:], [(22, 'T1', '/<r1>/', '='),
                                      (23, '/<i3>/', 'T1', '=')])

    def test_while_y_exportacion_con_errores_semanticos(self):
        for operador, destino_v, destino_f in [('&&', '5', '13'), ('||', '9', '5')]:
            codigo = f'while (/<x>/ < 5 {operador} /<y>/ > 2) {{ /<x>/++; }}'
            self.assertTrue(analizar(codigo).errores)
            filas = generar_triplos(codigo)
            self.assertEqual(filas[2:4], [(3, '', 'TRUE', destino_v),
                                         (4, '', 'FALSE', destino_f)])
            self.assertEqual(filas[-1], (12, '', '1', 'JMP'))
            with TemporaryDirectory() as carpeta:
                ruta = Path(carpeta) / 'resultado.txt'
                guardar_txt(ruta, filas)
                with ruta.open(encoding='utf-8-sig', newline='') as archivo:
                    tabla = list(csv.reader(archivo, delimiter='\t'))
                self.assertEqual(tabla[0], ['Renglón', 'Dato objeto', 'Dato fuente', 'Operador'])
                self.assertEqual(tabla[1:], [list(map(str, f)) for f in filas])

    def test_funcion_sin_parametros_y_jerarquia(self):
        filas = generar_triplos('phi /<Calcular>/() { /<x>/ = 5 + 3 * 2; '
                                'return /<x>/; } /<r>/ = /<Calcular>/();')
        self.assertIn((4, 'T2', '2', '*'), filas)
        self.assertEqual(filas[-3:], [(8, '', '2', 'JMP'), (9, 'T1', '/<x>/', '='),
                                     (10, '/<r>/', 'T1', '=')])
