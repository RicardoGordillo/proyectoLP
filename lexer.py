# lexer.py

# Analizador lexico de Ruby con PLY (lex)
# Avance 1 - Seccion: Variables e identificadores

import os
import argparse
from datetime import datetime
import ply.lex as lex


# Inicio aporte: Variables e identificadores  (integrante: Ricardo Gordillo)


reserved = {
    "self": "SELF",
    "nil": "NIL",
    "true": "TRUE",
    "false": "FALSE",
}


tokens = (
    # Variables y constantes
    "ID",              # variable local:        total, _x, edad2
    "VAR_INSTANCIA",   # variable de instancia: @nombre
    "VAR_CLASE",       # variable de clase:     @@contador
    "VAR_GLOBAL",      # variable global:       $estado
    "CONSTANTE",       # constante:             LIMITE, IVA
    #Base agregada para poder hacer asignaciones (Borren este comentario y esta parte cuando agreguen estas operaciones, esto lo agregue para hacer pruebas)
    "ASSIGN",
    "NUMBER",
    "FLOAT",
    "PLUS", "MINUS", "TIMES", "DIVIDE", "MOD",
    "LPAREN", "RPAREN",
) + tuple(reserved.values())

# --- Tokens simples ---
t_ASSIGN = r"="
t_PLUS = r"\+"
t_MINUS = r"-"
t_TIMES = r"\*"
t_DIVIDE = r"/"
t_MOD = r"%"
t_LPAREN = r"\("
t_RPAREN = r"\)"


# --- Tokens con funcion ---


def t_VAR_CLASE(t):
    r"@@[a-zA-Z_][A-Za-z0-9_]*"
    return t


def t_VAR_INSTANCIA(t):
    r"@[a-zA-Z_][A-Za-z0-9_]*"
    return t


def t_VAR_GLOBAL(t):
    r"\$[a-zA-Z_][A-Za-z0-9_]*"
    return t


def t_CONSTANTE(t):
    r"[A-Z][A-Za-z0-9_]*"
    return t


def t_ID(t):
    r"[a-z_][A-Za-z0-9_]*"
    # Si el texto es self/nil/true/false, cambia el tipo, si no, es variable local
    t.type = reserved.get(t.value, "ID")
    return t

# Fin aporte: Variables e identificadores



# --- Numeros (borren este comentario, lo agregue para poder hacer asignaciones basicas)---
def t_FLOAT(t):
    r"\d+\.\d+"
    t.value = float(t.value)
    return t


def t_NUMBER(t):
    r"\d+"
    t.value = int(t.value)
    return t


def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


# Caracteres ignorados (espacios y tabs)
t_ignore = " \t"

errores = []


def t_error(t):
    msg = f"Error lexico, linea {t.lexer.lineno}: caracter no definido en el lenguaje '{t.value[0]}'"
    errores.append(msg)
    print(msg)
    t.lexer.skip(1)


lexer = lex.lex()


def analizar(codigo):
    errores.clear()
    lexer.lineno = 1
    lexer.input(codigo)
    salida = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        salida.append(f"Linea {tok.lineno}: {tok.type} - {tok.value!r}")
    return salida, list(errores)


def guardar_log(tokens_salida, errores_salida, usuario, carpeta="logs"):
    os.makedirs(carpeta, exist_ok=True)
    marca = datetime.now().strftime("%d-%m-%Y-%Hh%M")
    ruta = os.path.join(carpeta, f"lexico-{usuario}-{marca}.txt")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("=== TOKENS RECONOCIDOS ===\n")
        f.write("\n".join(tokens_salida) + "\n\n")
        f.write("=== ERRORES LEXICOS ===\n")
        f.write("\n".join(errores_salida) if errores_salida else "Ninguno")
        f.write("\n")
    return ruta


def probar(archivo, usuario):
    with open(archivo, encoding="utf-8") as f:
        codigo = f.read()
    toks, errs = analizar(codigo)
    print(f"\n--- {archivo} ({usuario}) ---")
    print("\n".join(toks))
    print(f"Log guardado en: {guardar_log(toks, errs, usuario)}")
 
 
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analizador lexico de Ruby (PLY)")
    parser.add_argument("archivos", nargs="+", help="uno o mas archivos .rb de prueba")
    parser.add_argument("-u", "--usuario", required=True, help="usuario de Git (va en el nombre del log)")
    args = parser.parse_args()
    for archivo in args.archivos:
        probar(archivo, args.usuario)