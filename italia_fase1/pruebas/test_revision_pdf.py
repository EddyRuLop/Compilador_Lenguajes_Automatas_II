"""Revisión de entrega: ejecutar manualmente desde la carpeta del proyecto."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from analizador import analizar


def filas(resultado):
    salida, i = [], 0
    while i < len(resultado.errores):
        error = resultado.errores[i]
        salida.append((error['Lexema'], error['Renglón'], error['Descripción']))
        i += 1
    return salida


class RevisionPDF(unittest.TestCase):
    def test_ejercicio_pdf_I_pagina_61(self):
        codigo = '''phi /<vUno>/, /<vDos>/, /<vTres>/;
rho /<vCuatro>/, /<vCinco>/, /<vSeis>/;
delta /<vSiete>/, /<vOcho>/, /<vNueve>/;
/<vUno>/ = 1 + 3.14 + 4;
/<vSiete>/ = /<vOcho>/ + /<vDos>/;
/<vCuatro>/ = 3.14 * 4 + 3.14 / 1;
/<vCuatro>/ = 1 - 21.14 * "c";
/<vTres>/ = /<vDos>/ + /<vUno>/;
/<vUno>/ = /<vSiete>/;
/<vCuatro>/ = /<vCinco>/ - /<vSeis>/;
/<vSiete>/ = /<vOcho>/ + /<vNueve>/;
/<vUno>/ = 3.14 + "z";
/<vCuatro>/ = 1 - 21.14 * "c";
/<vCuatro>/ = /<vOcho>/;'''
        r = analizar(codigo)
        self.assertFalse(r.observaciones)
        self.assertEqual(filas(r), [
            ('3.14', 4, 'Incompatibilidad de tipos, phi'),
            ('/<vDos>/', 5, 'Incompatibilidad de tipos, delta'),
            ('"c"', 7, 'Incompatibilidad de tipos, rho'),
            ('/<vSiete>/', 9, 'Incompatibilidad de tipos, phi'),
            ('3.14', 12, 'Incompatibilidad de tipos, phi'),
            ('"z"', 12, 'Incompatibilidad de tipos, phi'),
            ('"c"', 13, 'Incompatibilidad de tipos, rho'),
            ('/<vOcho>/', 14, 'Incompatibilidad de tipos, rho')])

    def test_pdf_III_pagina_9(self):
        r = analizar('phi /<Uno>/, /<Dos>/\n/<Uno>/ = 25.5 * 10 / 52;\n'
                     '/<Dos>/ = 10 + 52 - 3.14;\n/<tres>/ = "ejemplo";')
        self.assertFalse(r.observaciones)
        self.assertEqual(filas(r), [
            ('25.5', 2, 'Incompatibilidad de tipos, phi'),
            ('/', 2, 'Incompatibilidad de tipos, phi'),
            ('3.14', 3, 'Incompatibilidad de tipos, phi'),
            ('/<tres>/', 4, 'Variable indefinida')])
        self.assertIn({'Lexema': '/<tres>/', 'Tipo': ''}, r.simbolos)

    def test_pdf_III_pagina_11(self):
        r = analizar('phi /<Uno>/, /<Dos>/;\nrho /<tres>/;\n'
                     '/<Uno>/ = 25.5 * 10 / 52;\n/<Dos>/ = 10 + 52 - 3.14;\n'
                     '/<tres>/ = /<ejemplo>/;')
        self.assertFalse(r.observaciones)
        self.assertEqual(filas(r), [
            ('25.5', 3, 'Incompatibilidad de tipos, phi'),
            ('/', 3, 'Incompatibilidad de tipos, phi'),
            ('3.14', 4, 'Incompatibilidad de tipos, phi'),
            ('/<ejemplo>/', 5, 'Variable indefinida')])

    def test_pdf_III_pagina_15_aplica_tambien_reglas_pdf_I(self):
        # La diapositiva destaca el return, pero también contiene una cadena
        # asignada a float. Se conserva esa incompatibilidad según el PDF I.
        r = analizar('phi /<Uno>/, /<Dos>/;\nrho /<tres>/;\n'
                     'phi /<Otro>/()\n{\nreturn /<tres>/ * 52;\n}\n'
                     '/<Uno>/ = 25.5 * 10 / 52;\n/<Dos>/ = 10 - 3;\n'
                     '/<tres>/ = "ejemplo";\n/<Uno>/ = /<Otro>/();')
        self.assertFalse(r.observaciones)
        self.assertEqual(filas(r), [
            ('/<tres>/', 5, 'Incompatibilidad de tipos, phi'),
            ('25.5', 7, 'Incompatibilidad de tipos, phi'),
            ('/', 7, 'Incompatibilidad de tipos, phi'),
            ('"ejemplo"', 9, 'Incompatibilidad de tipos, rho')])

    def test_ejemplos_en_carpeta_separada(self):
        carpeta = Path(__file__).parent / 'ejemplos'
        casos = [('00_ejemplo_anterior.txt', 0), ('01_correcto.txt', 0),
                 ('02_actividad_con_errores.txt', 14), ('03_prioridades_pdf_III.txt', 7),
                 ('05_funciones_correctas.txt', 0), ('06_funciones_errores_pdf_III.txt', 11)]
        i = 0
        while i < len(casos):
            nombre, cantidad = casos[i]
            with self.subTest(archivo=nombre):
                r = analizar((carpeta / nombre).read_text(encoding='utf-8'))
                self.assertEqual(len(r.errores), cantidad)
                self.assertFalse(r.observaciones)
            i += 1
        r = analizar((carpeta / '04_entrada_mal_escrita.txt').read_text(encoding='utf-8'))
        self.assertEqual(len(r.errores), 2)
        self.assertTrue(r.observaciones)

    def test_limites_justo_antes_y_despues(self):
        self.assertFalse(analizar('#' + 'a' * 249999).observaciones)
        self.assertTrue(analizar('#' + 'a' * 250000).observaciones)
        self.assertFalse(analizar(';' * 50000).observaciones)
        self.assertTrue(analizar(';' * 50001).observaciones)

    def test_programa_independiente_de_la_carpeta_pruebas(self):
        # Se copian únicamente los módulos de la aplicación a otra carpeta.
        # Importar main no debe abrir la ventana ni ejecutar las pruebas.
        origen = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temporal:
            archivos, i = list(origen.glob('*.py')), 0
            while i < len(archivos):
                shutil.copy2(archivos[i], temporal)
                i += 1
            codigo = ('import main; from analizador import analizar; '
                      'r=analizar("phi /<n>/; /<n>/=1;"); '
                      'assert not r.errores and not r.observaciones; '
                      'r=analizar(""); '
                      'assert not r.simbolos and not r.errores and not r.observaciones')
            p = subprocess.run([sys.executable, '-B', '-c', codigo], cwd=temporal,
                               capture_output=True, text=True, timeout=15)
            self.assertEqual(p.returncode, 0, p.stderr)


if __name__ == '__main__':
    unittest.main()
