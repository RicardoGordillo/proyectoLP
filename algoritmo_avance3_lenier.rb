# Las dos clases pueden definir IVA. Leer IVA tampoco cuenta como asignación.
class Compra
  IVA = 0.15
  puts IVA
end

class Venta
  IVA = 0.12
end

puts IVA
IVA = 0.15
precio = 2 + 1.5
saludo = "Hola, " + "Ruby"

# Las entradas, las llamadas y los tipos que difieren entre ramas son desconocidos.
entrada = gets
desde_llamada = convertir(entrada)
puts "Entrada: " + entrada
puts "Resultado: " + desde_llamada
if entrada
  dato = 2
else
  dato = "dos"
end
puts "Dato: " + dato

# Errores esperados: dos reasignaciones y dos operaciones incompatibles.
IVA = 0.12
IVA += 0.01
cantidad = 2
total = "5" +
  cantidad
activo = true
resultado = activo + 1
