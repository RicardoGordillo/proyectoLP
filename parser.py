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
    
# Ricardo Gordillo — Asignación compuesta (+=, -=, *=, /=).
def p_asignacion_compuesta(p):
    "expresion : ID op_asig_compuesta saltos expresion %prec ASSIGN"
    p[0] = ("asignacion_compuesta", p[2], p[1], p[4])

def p_op_asig_compuesta(p):
    """op_asig_compuesta : PLUS_ASSIGN
                         | MINUS_ASSIGN
                         | TIMES_ASSIGN
                         | DIVIDE_ASSIGN"""
    p[0] = p[1]

# Ricardo Gordillo — Estructura while ... end.
def p_while(p):
    "expresion : WHILE expresion inicio_while cuerpo END"
    p[0] = ("while", p[2], p[4])


def p_inicio_while(p):
    """inicio_while : separador
                    | DO"""
                    
# Ricardo Gordillo - Estructura hash arrow (=>) para definir hashes.
def p_hash(p):
    "expresion : LBRACE saltos pares_optativos RBRACE"
    p[0] = ("hash", p[3])
    
def p_pares_optativos(p):
    """pares_optativos : vacio
                       | pares saltos
                       | pares COMMA saltos"""
    p[0] = [] if len(p) == 2 else p[1]

def p_pares(p):
    """pares : par
             | pares COMMA saltos par"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[4])
        p[0] = p[1]

def p_par(p):
    "par : expresion HASH_ARROW saltos expresion"
    p[0] = ("par", p[1], p[4])
    
# Ricardo Gordillo - Funcion lambda (->) para definir funciones anónimas.
def p_lambda(p):
    "expresion : LAMBDA LPAREN saltos parametros RPAREN saltos LBRACE cuerpo RBRACE"
    p[0] = ("lambda", p[4], p[8])
    
# Ricardo Gordillo - Llamada a métodos con punto (.) y argumentos opcionales.
def p_llamada_metodo(p):
    """expresion : expresion DOT ID
                 | expresion DOT ID LPAREN saltos argumentos_optativos RPAREN"""
    p[0] = ("metodo", p[1], p[3], p[6] if len(p) == 8 else [])
 
# Ricardo Gordillo - Impresion de expresiones con puts y print.   
def p_impresion(p):
    """sentencia : PUTS
                 | PRINT
                 | PUTS argumentos
                 | PRINT argumentos"""
    p[0] = ("impresion", p[1], p[2] if len(p) == 3 else [])
    
# Ricardo Gordillo - Lectura de expresiones con gets.
def p_entrada(p):
    "expresion : GETS"
    p[0] = ("entrada", p[1])

# Ricardo Gordillo - variables de instancia, clase, globales y constantes.
def p_variable_especial(p):
    """variable_especial : VAR_INSTANCIA
                         | VAR_CLASE
                         | VAR_GLOBAL
                         | CONSTANTE"""
    p[0] = (p.slice[1].type.lower(), p[1])

def p_referencia_especial(p):
    "expresion : variable_especial"
    p[0] = p[1]

def p_asignacion_especial(p):
    "expresion : variable_especial ASSIGN saltos expresion"
    p[0] = ("asignacion_" + p[1][0], p[1][1], p[4])

def p_asignacion_compuesta_especial(p):
    "expresion : variable_especial op_asig_compuesta saltos expresion %prec ASSIGN"
    p[0] = ("asignacion_compuesta", p[2], p[1], p[4])

def p_self(p):
    "expresion : SELF"
    p[0] = ("self",)

def p_simbolo(p):
    "expresion : SIMBOLO"
    p[0] = ("simbolo", p[1])
   
# Ricardo Gordillo - Clase (con herencia opcional) y metodos sin parentesis
def p_clase(p):
    """sentencia : CLASS CONSTANTE cuerpo END
                 | CLASS CONSTANTE LT CONSTANTE cuerpo END"""
    if len(p) == 5:
        p[0] = ("clase", p[2], None, p[3])
    else:
        p[0] = ("clase", p[2], p[4], p[5])
        
def p_def_sin_parametros(p):
    "sentencia : DEF ID separador cuerpo END"
    p[0] = ("def", p[2], [], p[4])
    
# Ricardo Gordillo - propiedades: attr_accessor, attr_reader, attr_writer
def p_propiedades(p):
    """sentencia : ATTR_ACCESSOR lista_simbolos
                 | ATTR_READER lista_simbolos
                 | ATTR_WRITER lista_simbolos"""
    p[0] = ("propiedad", p[1], p[2])

def p_lista_simbolos(p):
    """lista_simbolos : SIMBOLO
                      | lista_simbolos COMMA saltos SIMBOLO"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[4])
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
