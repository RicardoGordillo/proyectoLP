# Ricardo Gordillo
# Todo lo de este archivo debe ser reconocido sin errores sintacticos


# Asignacion compuesta 
contador = 10
contador += 5
contador -= 3
contador *= 2
contador /= 4
total = 0
total += contador * 2 + 1
precio = 12.5
precio *= 2

# while 
indice = 1
while indice <= 3
  total += indice
  indice += 1
end

while indice < 6 do
  indice += 1
end

while total > 100 && indice != 0; total -= 10; end

fila = 1
while fila <= 2
  columna = 1
  while columna <= 2
    columna += 1
  end
  fila += 1
end

# Hash
vacio = {}
persona = {"nombre" => "Ana", "edad" => 20}
notas = {"matematica" => 9, "fisica" => 8}
calculos = {"suma" => 2 + 3, "producto" => 4 * 5}
anidado = {"persona" => {"nombre" => "Luis", "edad" => 25}}
con_array = {"lista" => [1, 2, 3]}
multilinea = {
  "a" => 1,
  "b" => 2,
}

# Lambda
doble = ->(x) { x * 2 }
suma = ->(a, b) { a + b }
saludo = ->() { "hola" }
positivo = ->(n) { n > 0 && n < 100 }
incrementar = ->(x) { x += 1 }
dos_pasos = ->(x) { y = x + 1; y * 2 }
resultado = doble.call(4)
total_suma = suma.call(2, 3) + 1
texto = saludo.call()
puts(doble.call(10))
operaciones = {"doble" => ->(x) { x * 2 }, "triple" => ->(x) { x * 3 }}

# Mezcla de las cuatro
n = 1
acumulado = 0
while n <= 3
  acumulado += doble.call(n)
  n += 1
end
puts(acumulado)
