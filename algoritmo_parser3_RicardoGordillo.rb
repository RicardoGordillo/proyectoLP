# Ricardo Gordillo
# El parser se detiene en el primer error,
# asi que el log solo mostrara el error de la ultima linea.

contador = 0
while contador < 3
  contador += 1
end
contador *= 2

# esperado: token inesperado PLUS_ASSIGN ('+=')
# 5 += 1

# OTROS CASOS INCORRECTOS:

# ASIGNACION COMPUESTA
# contador += += 2              # PLUS_ASSIGN inesperado
# contador **= 2                # ASSIGN inesperado (**= no esta en el subconjunto)
# contador %= 2                 # ASSIGN inesperado (%= no esta en el subconjunto)

# WHILE (cada uno en su propio archivo, son de varias lineas)
# while                         # NEWLINE inesperado (falta la condicion)
#   contador += 1
# end

# while contador < 3            # fin de archivo inesperado (falta end)
#   contador += 1
#
# end                           # END inesperado (end sin while)

# until contador > 3            # UNTIL inesperado (no esta soportado)
#  contador += 1
# end

# while contador < 3 then       # THEN inesperado (then no se usa en while)
#   contador += 1
# end

# AUN NO SOPORTADOS POR EL PARSER (fallan aunque sean Ruby correcto):
while contador < 3
  break                       # BREAK inesperado (falta la regla de break/next)
end
puts contador                 # ID inesperado (falta la regla de impresion)