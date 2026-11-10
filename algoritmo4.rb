# Prueba de palabras reservadas, delimitadores y comentarios de Adrian Toledo.
=begin
Este comentario de bloque contiene simbolos que no deben producir tokens: ~ ?
=end

def evaluar(edad = 18)
  valores = [1, 2, 3]; datos = {1 => 2}
  unless edad >= 18
    return false
  else
    return true
  end
end

edad, limite = 15, 18
resultado = evaluar(edad)
rango = 1..10 # Los puntos aun no estan implementados en el lexer.
