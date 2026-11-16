"""Reglas semánticas del Avance 3 sobre el AST de Ruby."""

import argparse
from datetime import datetime
from pathlib import Path

from parser import analizar_ast


TIPOS_LITERAL = {int: "Integer", float: "Float", bool: "Boolean", type(None): "NilClass"}
TIPOS_NODO = {
    "cadena": "String",
    "array": "Array",
    "hash": "Hash",
    "simbolo": "Symbol",
    "rango": "Range",
}
NUMERICOS = {"Integer", "Float"}
ARITMETICOS = {"+", "-", "*", "/", "%", "**"}
CORTOCIRCUITO = {"&&", "||", "and", "or"}


def _conservar_tipos(tipos, caminos):
    comunes = {
        nombre: tipo
        for nombre, tipo in caminos[0].items()
        if tipo is not None and all(camino.get(nombre) == tipo for camino in caminos[1:])
    }
    tipos.clear()
    tipos.update(comunes)


def _locales_modificadas(nodo):
    """Encuentra escrituras locales que pueden repetirse dentro de un while."""
    if isinstance(nodo, list):
        for hijo in nodo:
            yield from _locales_modificadas(hijo)
    elif isinstance(nodo, tuple):
        clase = nodo[0]
        if clase in {"def", "clase", "lambda"}:
            return
        if clase == "asignacion":
            yield nodo[1]
        elif clase == "asignacion_compuesta" and isinstance(nodo[2], str):
            yield nodo[2]
        elif clase == "asignacion_multiple":
            yield from nodo[1]
        for hijo in nodo[1:]:
            yield from _locales_modificadas(hijo)


class _Analizador:
    def __init__(self, lineas):
        self.lineas = lineas
        self.errores = []
        self.constantes = {}

    def error(self, nodo, regla, mensaje):
        linea = self.lineas[id(nodo)]
        self.errores.append(f"Error semántico ({regla}), línea {linea}: {mensaje}.")

    # Regla 1 de Lenier González Prieto: asignación a constantes.
    def asignar_constante(self, nodo, nombre, ambito):
        definidas = self.constantes.setdefault(ambito, set())
        if nombre in definidas:
            self.error(
                nodo, "asignación a constantes",
                f"la constante {nombre} ya fue definida y no puede reasignarse",
            )
        definidas.add(nombre)

    # Regla 2 de Lenier González Prieto: operaciones permitidas.
    def aritmetica(self, nodo, operador, izquierdo, derecho):
        if izquierdo is None or derecho is None:
            return None
        if izquierdo in NUMERICOS and derecho in NUMERICOS:
            # La potencia también puede devolver Rational o Complex.
            if operador == "**":
                return None
            return "Float" if "Float" in (izquierdo, derecho) else "Integer"
        if izquierdo == "String":
            if (operador == "+" and derecho == "String") or operador == "%":
                return "String"
            if operador == "*" and derecho in NUMERICOS:
                return "String"
        if izquierdo == "Array":
            if operador in {"+", "-"} and derecho == "Array":
                return "Array"
            if operador == "*":
                if derecho == "String":
                    return "String"
                if derecho in NUMERICOS:
                    return "Array"
        self.error(
            nodo, "operaciones permitidas",
            f"el operador {operador!r} no admite {izquierdo} con {derecho}",
        )
        return None

    def ramas(self, ramas, alternativa, tipos, ambito):
        caminos = []
        resultados = []
        restantes = tipos.copy()
        for condicion, cuerpo in ramas:
            self.visitar(condicion, restantes, ambito)
            locales = restantes.copy()
            resultados.append(self.visitar(cuerpo, locales, ambito))
            caminos.append(locales)
        resultados.append(self.visitar(alternativa, restantes, ambito))
        caminos.append(restantes)
        _conservar_tipos(tipos, caminos)
        if all(resultado == resultados[0] for resultado in resultados[1:]):
            return resultados[0]
        return None

    def visitar(self, nodo, tipos, ambito):
        if isinstance(nodo, list):
            tipo = None
            for hijo in nodo:
                tipo = self.visitar(hijo, tipos, ambito)
            return tipo
        if not isinstance(nodo, tuple):
            return None

        clase = nodo[0]
        if clase == "literal":
            return TIPOS_LITERAL[type(nodo[1])]
        if clase == "id":
            return tipos.get(nodo[1])
        if clase == "asignacion":
            tipo = self.visitar(nodo[2], tipos, ambito)
            tipos[nodo[1]] = tipo
            return tipo
        if clase == "asignacion_constante":
            self.asignar_constante(nodo, nodo[1], ambito)
            return self.visitar(nodo[2], tipos, ambito)
        if clase == "asignacion_compuesta":
            _, operador, destino, valor = nodo
            if isinstance(destino, str):
                izquierdo = tipos.get(destino)
                derecho = self.visitar(valor, tipos, ambito)
                tipo = self.aritmetica(nodo, operador[:-1], izquierdo, derecho)
                tipos[destino] = tipo
                return tipo
            if destino[0] == "constante":
                self.asignar_constante(nodo, destino[1], ambito)
            self.visitar(valor, tipos, ambito)
            return None
        if clase == "asignacion_multiple":
            self.visitar(nodo[2], tipos, ambito)
            for nombre in nodo[1]:
                tipos.pop(nombre, None)
            return None
        if clase == "binaria":
            _, operador, izquierda, derecha = nodo
            izquierdo = self.visitar(izquierda, tipos, ambito)
            if operador in CORTOCIRCUITO:
                ejecutado = tipos.copy()
                derecho = self.visitar(derecha, ejecutado, ambito)
                _conservar_tipos(tipos, [tipos, ejecutado])
                return izquierdo if izquierdo == derecho else None
            derecho = self.visitar(derecha, tipos, ambito)
            if operador in ARITMETICOS:
                return self.aritmetica(nodo, operador, izquierdo, derecho)
            return None
        if clase == "unaria":
            _, operador, expresion = nodo
            tipo = self.visitar(expresion, tipos, ambito)
            if operador in {"!", "not"}:
                return "Boolean"
            if tipo is not None and tipo not in NUMERICOS | {"String"}:
                self.error(nodo, "operaciones permitidas", f"el operador {operador!r} no admite {tipo}")
                return None
            return tipo
        if clase == "if":
            _, condicion, cuerpo, elsif, alternativa = nodo
            ramas = [(condicion, cuerpo)] + [(rama[1], rama[2]) for rama in elsif]
            return self.ramas(ramas, alternativa, tipos, ambito)
        if clase == "unless":
            _, condicion, cuerpo, alternativa = nodo
            return self.ramas([(condicion, cuerpo)], alternativa, tipos, ambito)
        if clase == "else":
            return self.visitar(nodo[1], tipos, ambito)
        if clase == "while":
            _, condicion, cuerpo = nodo
            self.visitar(condicion, tipos, ambito)
            for nombre in _locales_modificadas([condicion, cuerpo]):
                tipos.pop(nombre, None)
            self.visitar(cuerpo, tipos.copy(), ambito)
            return None
        if clase == "clase":
            self.visitar(nodo[3], {}, ambito + (nodo[1],))
            return None
        if clase in {"def", "lambda"}:
            locales = {}
            # El parser admite asignaciones en def. Su cuerpo se analiza aparte.
            ambito_cuerpo = ambito + (id(nodo),) if clase == "def" else ambito
            for parametro in nodo[-2]:
                if isinstance(parametro, tuple):
                    self.visitar(parametro[2], locales, ambito_cuerpo)
            self.visitar(nodo[-1], locales, ambito_cuerpo)
            return "Proc" if clase == "lambda" else None
        for hijo in nodo[1:]:
            self.visitar(hijo, tipos, ambito)
        return TIPOS_NODO.get(clase)


def analizar(codigo):
    """Devuelve los diagnósticos de la primera fase que encuentre errores."""
    lineas = {}
    arbol, errores = analizar_ast(codigo, lineas=lineas)
    if errores:
        return errores
    analizador = _Analizador(lineas)
    analizador.visitar(arbol, {}, ())
    return analizador.errores


def probar(archivo):
    """Analiza un archivo, muestra su resultado y guarda el log de la ejecución."""
    try:
        errores = analizar(archivo.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as error:
        errores = [f"Error al leer el archivo: {error}"]
    resultado = errores or ["Análisis semántico correcto."]
    salida = "\n".join([f"Archivo analizado: {archivo}", *resultado])

    carpeta = Path("logs")
    carpeta.mkdir(exist_ok=True)
    nombre = datetime.now().strftime("semantico-LenierGlez-%d%m%Y-%Hh%M")
    ruta = carpeta / f"{nombre}.txt"
    indice = 2
    while True:
        try:
            with ruta.open("x", encoding="utf-8") as log:
                log.write(salida + "\n")
            break
        except FileExistsError:
            ruta = carpeta / f"{nombre}-{indice}.txt"
            indice += 1

    print(salida)
    print(f"Log guardado en: {ruta}")
    return not errores


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description="Analizador semántico de Ruby (Avance 3)")
    cli.add_argument("archivos", type=Path, nargs="+", help="archivos Ruby de prueba")
    args = cli.parse_args()
    resultados = [probar(archivo) for archivo in args.archivos]
    raise SystemExit(0 if all(resultados) else 1)
