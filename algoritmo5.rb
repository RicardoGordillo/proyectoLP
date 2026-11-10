# Prueba de palabras reservadas y delimitadores (Adrian Toledo).
BEGIN { inicio = true }
def clasificar(valor = nil)
  if defined?(valor) and not false
    [valor, __LINE__]; {1 => 2}
  else
    return nil
  end
end
