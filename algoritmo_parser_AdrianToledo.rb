# Adrián Toledo: asignación múltiple, rangos, unless y parámetros por defecto.
x, y = 10, 20
nombre, activo = "Adrian", true
base, altura = 5.0, 12.0
rango_inclusivo = 1..10
rango_exclusivo = 0...100
letras = "a".."z"
unless x >= 18
  puts "Acceso restringido"
else
  puts "Bienvenido"
end

def saludar(nombre = "Invitado")
  return "Hola, " + nombre
end
mensaje1 = saludar()
mensaje2 = saludar("Adrian")
