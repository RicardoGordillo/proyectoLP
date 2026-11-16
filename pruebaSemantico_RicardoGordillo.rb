# Reglas probadas: identificadores y estructuras de control (break / next).
# Este archivo no debe producir ningun error semantico.

LIMITE = 5
precio = 100
descuento = 10
total = precio - descuento
total *= 2
puts "Total: " + total.to_s

x, y = 10, 20
puts x + y

print "Ingrese su nombre: "
nombre = gets.chomp
puts "Hola, " + nombre

# break y next dentro de un while
contador = 0
while contador < LIMITE
  contador += 1
  if contador == 2
    next
  end
  if contador == 4
    break
  end
  puts contador
end

# while anidado: el contador de bucles sube a 2 y vuelve a 1
fila = 0
while fila < 3
  columna = 0
  while columna < 3
    columna += 1
    if columna == 2
      break
    end
  end
  fila += 1
end

# metodo con sus propias variables y un while dentro
def sumar_hasta(maximo)
  i = 0
  suma = 0
  while i < maximo
    i += 1
    if i == 3
      next
    end
    suma += i
  end
  return suma
end
resultado = sumar_hasta(5)
puts resultado

# lambda: si puede ver las variables de afuera
factor = 3
triple = ->(n) { n * factor }
puts triple.call(4)

# clase simple
class Persona
  attr_accessor :nombre
  def saludar(otro)
    return otro
  end
end

# estructuras de datos y condicionales
notas = [8, 9, 10]
persona = { "nombre" => "Ana", "edad" => 20 }
rango = 1..10
nota = 8
if nota >= 9
  puts "Excelente"
elsif nota >= 7
  puts "Aprobado"
else
  puts "Reprobado"
end
edad = 15
unless edad >= 18
  puts "Acceso restringido"
else
  puts "Bienvenido"
end
