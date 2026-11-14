# Ricardo Gordillo
# El parser se detiene en el primer error,
# asi que el log solo mostrara el error de la ultima linea.

datos = {"a" => 1, "b" => 2}
doble = ->(x) { x * 2 }
r = doble.call(3)

# esperado: token inesperado NUMBER (1)
# malo = {"a" 1}

# OTROS CASOS INCORRECTOS

# HASH
# malo = {"a" => }              # RBRACE inesperado (falta el valor)
# malo = {"a" => 1,, "b" => 2}  # COMMA inesperado (dos comas)
# malo = {, "a" => 1}           # COMMA inesperado (coma inicial)
# malo = {"a" => 1              # falta }: error en lo que siga o EOF
# malo = {:nombre => "Ana"}     # error LEXICO por ':' (simbolos no soportados)
#
# LAMBDA
# f = ->(x) x * 2               # ID inesperado (faltan las llaves)
# f = ->(x) { x * 2             # fin de archivo inesperado (falta })
# f = ->(x { x * 2 }            # LBRACE inesperado (falta el parentesis)
# f = (x) { x * 2 }             # LBRACE inesperado (falta la flecha ->)
# r = doble.call                # NEWLINE inesperado: valido en Ruby, pero tu
#                               # regla exige parentesis
#
# ACEPTADO A PROPOSITO (la sintaxis es correcta; lo rechazara el semantico):
r = doble.llamar(3)           # el parser NO falla, el segundo ID no es "call"
