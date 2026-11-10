# Analizador léxico de Ruby

## Ejecución

Instalar PLY y ejecutar el analizador con uno o más archivos Ruby:

```sh
pip install -r requirements.txt
python3 lexer.py algoritmo1.rb algoritmo2.rb algoritmo3.rb -u nombre_usuario
```

Cada archivo analizado genera un log en `logs/` con los tokens y errores. Si
se ejecutan varias pruebas en el mismo minuto, se agrega un número al nombre
del log para conservar todos los resultados.
