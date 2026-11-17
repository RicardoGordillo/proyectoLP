# Adrián Toledo: conversiones y coherencia de retorno.
cadena = "42"
numero = cadena.to_i
texto = numero.to_s
valido = true
invalido = valido.to_i

def calcular_area(base, altura)
  area = base * altura
  return area
end

def area_incorrecta(base, altura)
  return resultado
end

def resultados_incompatibles(numero)
  if numero > 0
    return numero + 1
  else
    return "sin valor"
  end
end
