# Avance 1: aporte de Lenier González (LenierGlez)

Grupo: Redstone — Ruby, PLY (`lex`). Repositorio de equipo: `RicardoGordillo/proyectoLP`.

## Relación con el documento Proyecto_LP_Parcial1

En la sección 6 (tabla de responsabilidades), el área léxica de Lenier comprende **identificadores, números y cadenas**. Ricardo ya aporta la base de identificadores; este commit completa y prueba **números enteros (`NUMBER`), decimales (`FLOAT`) y cadenas (`STRING`)** sin volver a implementar los identificadores existentes. Los identificadores se verifican por integración. En el primer avance **no se implementan** ni las reglas sintácticas de `if`, métodos y arreglos, ni las reglas semánticas de constantes y operaciones; corresponden a entregas posteriores.

## Archivos nuevos de Lenier

- `integrar_lenier.py`: integra la sección de Lenier en `lexer.py` existente conservando los aportes de Ricardo y Adrián. Este archivo solo debe ejecutarse una vez.
- `algoritmo7.rb`: asignaciones locales, enteros, decimales, cadenas y salida `puts`.
- `algoritmo8.rb`: expresiones aritméticas, enteros y decimales.
- `algoritmo9.rb`: cadenas entre comillas simples/dobles, escapes, operaciones y `puts`.
- `prueba_error_lenier.rb`: cadena sin cierre para registrar un error intencional.
- `pruebas/test_lenier.py`: 7 casos automatizados.
- `requirements.txt`: `ply==3.11`.
- `logs/lexico-LenierGlez-...`: se generan al ejecutar cada algoritmo desde tu equipo.

**No sobrescribir `algoritmo4.rb`, `algoritmo5.rb`, `algoritmo6.rb`: pertenecen a Adrián.**

## Prueba local

```powershell
py integrar_lenier.py
py -m unittest discover -s pruebas -p test_lenier.py -v
py lexer.py algoritmo7.rb algoritmo8.rb algoritmo9.rb prueba_error_lenier.rb -u LenierGlez
```

Deben aparecer al menos 3 nuevos logs `lexico-LenierGlez-fecha-hora.txt` en `logs`. Como la prueba de error es deliberadamente inválida, su log debe contener un error de cadena no cerrada. El código no ejecuta Ruby ni valida su sintaxis o semántica, únicamente reconoce tokens.

## Importante para los commits

Subir el `lexer.py` **integrado**, los cuatro `.rb` del aporte, los logs de Lenier generados, la prueba, la dependencia, el script y este documento. No subir `lexer_pre_lenier_backup.py` ni las copias locales. El commit debe hacerse desde la cuenta de GitHub `LenierGlez` con un correo asociado a esa cuenta.
