# lexer.py

# Analizador lexico de Ruby con PLY (lex)
# Avance 1 - Seccion: Variables e identificadores

import os
import argparse
import re
from datetime import datetime
import ply.lex as lex


# Inicio aporte: Variables e identificadores  (integrante: Ricardo Gordillo)


# Inicio aporte: palabras reservadas, delimitadores y comentarios (Adrian Toledo)
reserved = {
    palabra: palabra.upper() for palabra in (
        "alias", "and", "begin", "break", "case", "class", "def", "do",
        "else", "elsif", "end", "ensure", "for", "if", "in", "module",
        "next", "not", "or", "redo", "rescue", "retry", "return", "super",
        "then", "undef", "unless", "until", "when", "while", "yield",
    )
}
reserved.update({
    "self": "SELF",
    "nil": "NIL",
    "true": "TRUE",
    "false": "FALSE",
    "defined?": "DEFINED",
    "BEGIN": "BEGIN_UPPER",
    "END": "END_UPPER",
    "__FILE__": "FILE_MAGIC",
    "__LINE__": "LINE_MAGIC",
    "__ENCODING__": "ENCODING_MAGIC",
})
# Fin aporte: palabras reservadas (Adrian Toledo)


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
    "STRING",  # Lenier: cadenas Ruby simples y dobles
    "PLUS", "MINUS", "TIMES", "DIVIDE", "MOD",
    "LPAREN", "RPAREN",
    # Inicio aporte: delimitadores (Adrian Toledo)
    "LBRACKET", "RBRACKET", "LBRACE", "RBRACE", "COMMA", "SEMICOLON",
    # Fin aporte: delimitadores (Adrian Toledo)
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

# Inicio aporte: delimitadores y comentarios (Adrian Toledo)
t_LBRACKET = r"\["
t_RBRACKET = r"\]"
t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_COMMA = r","
t_SEMICOLON = r";"


def t_COMENTARIO_BLOQUE(t):
    r"(?m:^=begin(?=[ \t\r\n]|$)[^\n]*(?:\n|$))"
    inicio = t.lexpos
    fin = re.search(r"(?m:^=end(?=[ \t\r\n]|$)[^\n]*(?:\n|$))", t.lexer.lexdata[t.lexer.lexpos:])
    if fin is None:
        msg = f"Error lexico, linea {t.lineno}: comentario de bloque sin =end"
        errores.append(msg)
        print(msg)
        t.lexer.lexpos = len(t.lexer.lexdata)
    else:
        t.lexer.lexpos += fin.end()
    t.lexer.lineno += t.lexer.lexdata[inicio:t.lexer.lexpos].count("\n")


def t_COMENTARIO_LINEA(t):
    r"\#[^\n]*"
    pass


def t_DEFINED(t):
    r"defined\?(?![A-Za-z0-9_])"
    return t
# Fin aporte: delimitadores y comentarios (Adrian Toledo)


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
    t.type = reserved.get(t.value, "CONSTANTE")
    return t


def t_ID(t):
    r"[a-z_][A-Za-z0-9_]*"
    # Si el texto es self/nil/true/false, cambia el tipo, si no, es variable local
    t.type = reserved.get(t.value, "ID")
    return t

# Fin aporte: Variables e identificadores



# ===== INICIO APORTE: LENIER GONZALEZ (NUMEROS Y CADENAS) =====
# Números enteros, decimales y cadenas sin interpolacion (fase lexica).
# La regla de STRING debe reconocer todo el lexema como una sola pieza.
def t_STRING(t):
    r'''("(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*')'''
    return t


def t_FLOAT(t):
    r"[0-9]+\.[0-9]+"
    t.value = float(t.value)
    return t


def t_NUMBER(t):
    r"[0-9]+"
    t.value = int(t.value)
    return t
# ===== FIN APORTE: LENIER GONZALEZ (NUMEROS Y CADENAS) =====


def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


# Caracteres ignorados (espacios y tabs)
t_ignore = " \t\r"

errores = []


def t_error(t):
    # INICIO APORTE: LENIER GONZALEZ - cadena sin cerrar
    if t.value[0] in ('"', "'"):
        posicion_salto = t.value.find("\n")
        longitud = posicion_salto if posicion_salto >= 0 else len(t.value)
        msg = f"Error lexico, linea {t.lexer.lineno}: cadena sin comilla de cierre"
        errores.append(msg)
        print(msg)
        t.lexer.skip(max(1, longitud))
        return
    # FIN APORTE: LENIER GONZALEZ
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
    # No sobrescribir pruebas ejecutadas durante el mismo minuto.
    indice = 2
    while os.path.exists(ruta):
        ruta = os.path.join(carpeta, f"lexico-{usuario}-{marca}-{indice}.txt")
        indice += 1
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
