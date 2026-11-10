"""Pruebas unitarias del aporte lexico de Lenier. Ejecutar desde raiz con -m unittest."""
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lexer import analizar


class TestLexicoLenier(unittest.TestCase):
    def test_entero_y_decimal(self):
        resultado, errores = analizar("edad = 21\npromedio = 8.5\n")
        self.assertEqual(errores, [])
        self.assertTrue(any("NUMBER - 21" in t for t in resultado))
        self.assertTrue(any("FLOAT - 8.5" in t for t in resultado))

    def test_cadenas_comillas_y_escape(self):
        resultado, errores = analizar('nombre = "Lenier"\nciudad = \'Guayaquil\'\nsaludo = "Hola, \\"Ruby\\""')
        self.assertEqual(errores, [])
        self.assertEqual(sum(": STRING - " in t for t in resultado), 3)

    def test_reutiliza_identificadores_de_ricardo(self):
        resultado, errores = analizar("total = 8\nIVA = 12\n@nombre = nil\n")
        self.assertEqual(errores, [])
        for tipo in ("ID", "CONSTANTE", "VAR_INSTANCIA", "NIL"):
            self.assertTrue(any(f": {tipo} - " in t for t in resultado), tipo)

    def test_error_cadena_sin_cerrar_y_recuperacion(self):
        resultado, errores = analizar('mensaje = "Hola\nedad = 21\n')
        self.assertEqual(len(errores), 1)
        self.assertIn("cadena sin comilla de cierre", errores[0])
        self.assertTrue(any("Linea 2: NUMBER - 21" in t for t in resultado))

    def test_columnas_de_linea_y_reset(self):
        primero, errores_1 = analizar('a = 1\nb = "texto"\n')
        segundo, errores_2 = analizar('c = 2\n')
        self.assertEqual((errores_1, errores_2), ([], []))
        self.assertTrue(any("Linea 2: STRING" in t for t in primero))
        self.assertTrue(any("Linea 1: NUMBER - 2" in t for t in segundo))

    def test_espacios_y_saltos_windows(self):
        tokens, errores = analizar('edad = 20\r\nnombre = "Ruby"\r\n')
        self.assertEqual(errores, [])
        self.assertTrue(any("Linea 2: STRING" in t for t in tokens))

    def test_cadenas_no_interrumpidas_por_simbolos(self):
        tokens, errores = analizar('mensaje = "Hola #Mundo"\n')
        self.assertEqual(errores, [])
        self.assertTrue(any("STRING" in t for t in tokens))


if __name__ == "__main__":
    unittest.main()
