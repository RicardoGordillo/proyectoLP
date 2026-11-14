def resumen(nota, minimo)
  aprobada = nota >= minimo && nota <= 10
  if aprobada
    resultado = ["aprobada", nota]
  elsif nota < 0 then
    resultado = ["inválida", nil]
  elsif nota == 0
    resultado = ["sin puntaje", 0]
  else
    resultado = ["no aprobada", nota]
  end
  return resultado
end

base = 4; minimo = 7
nota = base + 2 ** 2 * 1.0
resultados = [
  resumen(nota, minimo),
  resumen(0, minimo),
  [],
]
