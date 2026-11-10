"""Integra solo el aporte de Lenier en lexer.py actual sin eliminar a otros autores.

Requisitos: ejecutar desde la raiz del repositorio proyectoLP con las reglas
actuales de Ricardo y Adrian presentes en lexer.py. No publica cambios Git.
"""
from pathlib import Path
import ast
import re
import shutil
import sys

ARCHIVO = Path(__file__).resolve().parent / "lexer.py"
INICIO = "# ===== INICIO APORTE: LENIER GONZALEZ (NUMEROS Y CADENAS) ====="
FIN = "# ===== FIN APORTE: LENIER GONZALEZ (NUMEROS Y CADENAS) ====="


def fallar(mensaje):
    raise SystemExit("ERROR: " + mensaje)


def main():
    if not ARCHIVO.is_file():
        fallar("No existe lexer.py en esta carpeta; copia este script a C:\\proyectoLP.")

    contenido = ARCHIVO.read_text(encoding="utf-8")
    if INICIO in contenido:
        print("El aporte de Lenier ya esta integrado. No se modifica lexer.py.")
        return

    if "Adrian Toledo" not in contenido or "def t_COMENTARIO_LINEA" not in contenido:
        fallar("lexer.py no contiene la contribucion de Adrian. Primero ejecuta: "
              "git restore --source=HEAD -- lexer.py")

    if "def t_VAR_CLASE" not in contenido or "def t_ID" not in contenido:
        fallar("lexer.py no contiene identificadores de Ricardo; no es seguro integrarlo.")
    if re.search(r"^def t_STRING\(", contenido, flags=re.M):
        fallar("Ya existe una regla t_STRING. Revisar manualmente para evitar duplicados.")

    # Solo cambia declaracion de token STRING, sin modificar tokens de los otros.
    patron_float = r'(?m)^(\s*"FLOAT",(?:[^\n]*)\n)'
    if len(re.findall(patron_float, contenido)) != 1:
        fallar("No pude encontrar exactamente una declaracion FLOAT en tokens.")
    contenido = re.sub(patron_float,
        lambda m: m.group(1) + '    "STRING",  # Lenier: cadenas Ruby simples y dobles\n',
        contenido, count=1)

    # Sustituir solo reglas numericas provisionales por el aporte definitivo.
    numericas = re.compile(r'(?ms)^# --- Numeros[^\n]*---\s*\n.*?(?=^def t_newline\(t\):)')
    bloque = '''# ===== INICIO APORTE: LENIER GONZALEZ (NUMEROS Y CADENAS) =====
# Números enteros, decimales y cadenas sin interpolacion (fase lexica).
# La regla de STRING debe reconocer todo el lexema como una sola pieza.
def t_STRING(t):
    r\'''("(?:\\\\.|[^"\\\\\\n])*"|\'(?:\\\\.|[^\'\\\\\\n])*\')\'''
    return t


def t_FLOAT(t):
    r"[0-9]+\\.[0-9]+"
    t.value = float(t.value)
    return t


def t_NUMBER(t):
    r"[0-9]+"
    t.value = int(t.value)
    return t
# ===== FIN APORTE: LENIER GONZALEZ (NUMEROS Y CADENAS) =====


'''
    matches = list(numericas.finditer(contenido))
    if len(matches) != 1:
        fallar("No se encontro el bloque numerico provisional; detener para no pisar codigo.")
    contenido = numericas.sub(lambda _: bloque, contenido, count=1)

    # Permitir archivos CRLF de Windows; conserva las reglas originales.
    original_ignore = 't_ignore = " \\t"'
    if original_ignore in contenido:
        contenido = contenido.replace(original_ignore, 't_ignore = " \\t\\r"', 1)
    elif 't_ignore = " \\t\\r"' not in contenido:
        fallar("t_ignore no coincide con la forma esperada.")

    # Capturar error de cadena abierta sin quitar t_error preexistente.
    inicio_error = 'def t_error(t):\n'
    if contenido.count(inicio_error) != 1:
        fallar("No se encontro una sola funcion t_error.")
    error_lenier = '''def t_error(t):
    # INICIO APORTE: LENIER GONZALEZ - cadena sin cerrar
    if t.value[0] in ('"', "'"):
        posicion_salto = t.value.find("\\n")
        longitud = posicion_salto if posicion_salto >= 0 else len(t.value)
        msg = f"Error lexico, linea {t.lexer.lineno}: cadena sin comilla de cierre"
        errores.append(msg)
        print(msg)
        t.lexer.skip(max(1, longitud))
        return
    # FIN APORTE: LENIER GONZALEZ
'''
    contenido = contenido.replace(inicio_error, error_lenier, 1)

    # Antes de guardar, comprobar que el resultado sea Python valido.
    try:
        ast.parse(contenido, filename=str(ARCHIVO))
    except SyntaxError as exc:
        fallar(f"La integracion no compila; lexer.py sigue intacto: {exc}")

    copia = ARCHIVO.with_name("lexer_pre_lenier_backup.py")
    shutil.copy2(ARCHIVO, copia)
    ARCHIVO.write_text(contenido, encoding="utf-8")
    print("OK: Ricardo + Adrian + Lenier integrados en lexer.py")
    print(f"Respaldo local: {copia.name} (NO subir al repositorio)")
    print("Siguiente: py -m unittest discover -s pruebas -p test_lenier.py -v")


if __name__ == "__main__":
    main()
