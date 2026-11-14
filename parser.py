"""Analizador sintáctico del subconjunto de Ruby del Avance 2."""

import argparse
from datetime import datetime
from pathlib import Path
from pprint import pformat

import ply.yacc as yacc

import lexer as lexer_ruby
from lexer import tokens


start = "programa"

# PLY enumera los niveles desde la menor hasta la mayor precedencia.
precedence = (
    ("left", "AND", "OR"),
    ("right", "NOT"),
    ("right", "ASSIGN"),
    ("left", "OR_OP"),
    ("left", "AND_OP"),
    ("nonassoc", "EQ", "NEQ"),
    ("left", "GT", "GE", "LT", "LE"),
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE", "MOD"),
    ("right", "MENOS_UNARIO"),
    ("right", "POWER"),
    ("right", "NOT_OP", "MAS_UNARIO"),
)


def p_programa(p):
    "programa : cuerpo"
    p[0] = ("programa", p[1])


def p_cuerpo(p):
    "cuerpo : separadores_optativos sentencias"
    # La recursión derecha acumula las sentencias desde el final del cuerpo.
    p[2].reverse()
    p[0] = p[2]


def p_sentencias(p):
    """sentencias : vacio
                  | sentencia resto_sentencias"""
    if len(p) == 2:
        p[0] = []
    else:
        p[2].append(p[1])
        p[0] = p[2]


def p_resto_sentencias(p):
    """resto_sentencias : vacio
                        | separadores sentencias"""
    p[0] = p[2] if len(p) == 3 else []


def p_separadores_optativos(p):
    """separadores_optativos : vacio
                             | separadores"""


def p_separadores(p):
    """separadores : separador
                    | separadores separador"""


def p_separador(p):
    """separador : NEWLINE
                 | SEMICOLON"""


def p_saltos(p):
    """saltos : vacio
              | saltos NEWLINE"""


def p_vacio(p):
    "vacio :"


def p_sentencia(p):
    "sentencia : expresion"
    p[0] = p[1]


# Lenier González Prieto — Asignación local, literales y expresiones.
def p_asignacion(p):
    "expresion : ID ASSIGN saltos expresion"
    p[0] = ("asignacion", p[1], p[4])


def p_referencia(p):
    "expresion : ID"
    p[0] = ("id", p[1])


def p_literal_numerico(p):
    """expresion : NUMBER
                 | FLOAT"""
    p[0] = ("literal", p[1])


def p_literal_cadena(p):
    "expresion : STRING"
    # Las comillas y escapes del lexema conservan la sintaxis de Ruby.
    p[0] = ("cadena", p[1])


def p_literal_reservado(p):
    """expresion : NIL
                 | TRUE
                 | FALSE"""
    valores = {"nil": None, "true": True, "false": False}
    p[0] = ("literal", valores[p[1]])


def p_expresion_agrupada(p):
    "expresion : LPAREN saltos expresion saltos RPAREN"
    p[0] = p[3]


def p_expresion_binaria(p):
    """expresion : expresion PLUS saltos expresion
                 | expresion MINUS saltos expresion
                 | expresion TIMES saltos expresion
                 | expresion DIVIDE saltos expresion
                 | expresion MOD saltos expresion
                 | expresion POWER saltos expresion
                 | expresion EQ saltos expresion
                 | expresion NEQ saltos expresion
                 | expresion GT saltos expresion
                 | expresion GE saltos expresion
                 | expresion LT saltos expresion
                 | expresion LE saltos expresion
                 | expresion AND_OP saltos expresion
                 | expresion OR_OP saltos expresion
                 | expresion AND saltos expresion
                 | expresion OR saltos expresion"""
    p[0] = ("binaria", p[2], p[1], p[4])


def p_expresion_unaria(p):
    """expresion : MINUS saltos expresion %prec MENOS_UNARIO
                 | PLUS saltos expresion %prec MAS_UNARIO
                 | NOT_OP saltos expresion
                 | NOT saltos expresion"""
    p[0] = ("unaria", p[1], p[3])


# Lenier González Prieto — If con cualquier cantidad de elsif y else opcional.
def p_if(p):
    "expresion : IF expresion inicio_rama cuerpo ramas_if END"
    ramas_elsif, rama_else = p[5]
    ramas_elsif.reverse()
    p[0] = ("if", p[2], p[4], ramas_elsif, rama_else)


def p_inicio_rama(p):
    """inicio_rama : separador
                   | THEN
                   | separador THEN"""


def p_ramas_if(p):
    """ramas_if : vacio
                | ELSIF expresion inicio_rama cuerpo ramas_if
                | ELSE cuerpo"""
    if len(p) == 6:
        ramas_elsif, rama_else = p[5]
        ramas_elsif.append(("elsif", p[2], p[4]))
        p[0] = (ramas_elsif, rama_else)
    else:
        p[0] = ([], ("else", p[2]) if len(p) == 3 else None)


# Lenier González Prieto — Literales Array, con coma final opcional.
def p_array(p):
    "expresion : LBRACKET saltos argumentos_optativos RBRACKET"
    p[0] = ("array", p[3])


def p_argumentos_optativos(p):
    """argumentos_optativos : vacio
                            | argumentos saltos
                            | argumentos COMMA saltos"""
    p[0] = [] if len(p) == 2 else p[1]


def p_argumentos(p):
    """argumentos : expresion
                  | argumentos COMMA saltos expresion"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[4])
        p[0] = p[1]


# Lenier González Prieto — Métodos, parámetros, return y llamadas.
def p_def(p):
    "sentencia : DEF ID LPAREN saltos parametros RPAREN cuerpo END"
    p[0] = ("def", p[2], p[5], p[7])


def p_parametros(p):
    """parametros : vacio
                  | lista_parametros saltos"""
    p[0] = [] if len(p) == 2 else p[1]


def p_lista_parametros(p):
    """lista_parametros : ID
                        | lista_parametros COMMA saltos ID"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[4])
        p[0] = p[1]


def p_return(p):
    """sentencia : RETURN
                 | RETURN expresion"""
    p[0] = ("return", p[2] if len(p) == 3 else None)


def p_llamada(p):
    "expresion : ID LPAREN saltos argumentos_optativos RPAREN"
    p[0] = ("llamada", p[1], p[4])


def p_error(token):
    if token is None:
        raise SyntaxError("fin de archivo inesperado (EOF)")

    error = SyntaxError(f"token inesperado {token.type} ({token.value!r})")
    error.lineno = token.lineno
    raise error


# El lexer compartido contiene tokens de los demás aportes.
parser = yacc.yacc(debug=False, write_tables=False, errorlog=yacc.NullLogger())


def analizar_ast(codigo):
    """Devuelve (árbol, errores). Si hay errores, el árbol es None."""
    lexer_ruby.errores.clear()
    lexico = lexer_ruby.lexer.clone()
    lexico.lineno = 1
    try:
        arbol = parser.parse(codigo, lexer=lexico)
    except SyntaxError as error:
        linea = error.lineno if error.lineno is not None else codigo.count("\n") + 1
        diagnostico = f"Error sintáctico, línea {linea}: {error.msg}."
        return None, [*lexer_ruby.errores, diagnostico]

    errores = list(lexer_ruby.errores)
    return (None if errores else arbol), errores


def analizar(codigo):
    _, errores = analizar_ast(codigo)
    return errores


def probar(archivo, usuario):
    arbol, errores = analizar_ast(archivo.read_text(encoding="utf-8"))
    resultado = [f"Archivo analizado: {archivo}"]
    if errores:
        resultado.extend(errores)
    else:
        resultado.extend(["Análisis sintáctico correcto.", "AST:", pformat(arbol)])
    salida = "\n".join(resultado)

    carpeta = Path("logs")
    carpeta.mkdir(exist_ok=True)
    marca = datetime.now().strftime("%d-%m-%Y-%Hh%Mm%Ss%f")
    ruta = carpeta / f"sintactico-{usuario}-{marca}.txt"
    ruta.write_text(salida + "\n", encoding="utf-8")
    print(salida)
    print(f"Log guardado en: {ruta}")
    return not errores


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description="Analizador sintáctico de Ruby (PLY)")
    cli.add_argument("archivos", type=Path, nargs="+", help="archivos Ruby de prueba")
    cli.add_argument("-u", "--usuario", required=True, help="usuario de GitHub")
    args = cli.parse_args()
    resultados = [probar(archivo, args.usuario) for archivo in args.archivos]
    raise SystemExit(0 if all(resultados) else 1)
