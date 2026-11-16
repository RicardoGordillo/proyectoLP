"""Reglas semánticas del Avance 3 sobre el AST de Ruby."""

import argparse
from datetime import datetime
from pathlib import Path

from parser import analizar_ast

TIPOS_LITERAL = {
    int: "Integer",
    float: "Float",
    bool: "Boolean",
    type(None): "NilClass",
}
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
        if tipo is not None
        and all(camino.get(nombre) == tipo for camino in caminos[1:])
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
        self.bucles = 0
        self.alcances = [set()]

    def error(self, nodo, regla, mensaje):
        linea = self.lineas[id(nodo)]
        self.errores.append(f"Error semántico ({regla}), línea {linea}: {mensaje}.")

    # Ricardo Gordillo: reglas de identificadores
    def definir(self, nombre):
        self.alcances[-1].add(nombre)

    def usar(self, nodo, nombre):
        if nombre not in self.alcances[-1]:
            self.error(
                nodo, "identificador", f"la variable '{nombre}' no ha sido definida"
            )

    # Regla 1 de Lenier González Prieto: asignación a constantes.
    def asignar_constante(self, nodo, nombre, ambito):
        definidas = self.constantes.setdefault(ambito, set())
        if nombre in definidas:
            self.error(
                nodo,
                "asignación a constantes",
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
            nodo,
            "operaciones permitidas",
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
            self.usar(nodo, nodo[1])  # Ricardo Gordillo: verifica que este definida
            return tipos.get(nodo[1])

        if clase == "asignacion":
            tipo = self.visitar(nodo[2], tipos, ambito)
            self.definir(nodo[1])  # Ricardo Gordillo: define la variable
            tipos[nodo[1]] = tipo
            return tipo

        if clase == "asignacion_constante":
            self.asignar_constante(nodo, nodo[1], ambito)
            return self.visitar(nodo[2], tipos, ambito)

        if clase == "asignacion_compuesta":
            _, operador, destino, valor = nodo
            if isinstance(destino, str):
                self.usar(nodo, destino)
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
                self.definir(nombre)  # Ricardo Gordillo: define la variable
                tipos.pop(nombre, None)
            return None

        # Ricardo Gordillo: regla de break y next (solo puede usarse dentro de bucles)
        if clase in {"break", "next"}:
            if self.bucles == 0:
                self.error(
                    nodo,
                    "estructura de control",
                    f"{clase} solo puede usarse dentro de un bucle",
                )

            for hijo in nodo[1:]:
                self.visitar(hijo, tipos, ambito)
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
                self.error(
                    nodo,
                    "operaciones permitidas",
                    f"el operador {operador!r} no admite {tipo}",
                )
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
            self.bucles += 1
            self.visitar(cuerpo, tipos.copy(), ambito)
            self.bucles -= 1
            return None

        if clase == "clase":
            # Ricardo Gordillo: Dentro de una clase se resetean los bucles para que no se pueda hacer break o next y ademas se usa un set vacio para que no se pueda usar variables de afuera de la clase
            buclesprevios = self.bucles
            self.bucles = 0
            self.alcances.append(set())
            self.visitar(nodo[3], {}, ambito + (nodo[1],))
            self.alcances.pop()
            self.bucles = buclesprevios
            return None

        if clase in {"def", "lambda"}:
            # Ricardo Gordillo: dentro de un def o lambda no cuenta el while de afuera, así que break/next ahí son error
            locales = {}
            # El parser admite asignaciones en def. Su cuerpo se analiza aparte.
            ambito_cuerpo = ambito + (id(nodo),) if clase == "def" else ambito
            buclesprevios = self.bucles
            self.bucles = 0
            self.alcances.append(
                set() if clase == "def" else set(self.alcances[-1])
            )  # Ricardo Gordillo: Se crea un nuevo alcance para el def ya que un metodo no ve las variables de afuera
            for parametro in nodo[-2]:
                if isinstance(parametro, tuple):
                    self.visitar(parametro[2], locales, ambito_cuerpo)
                    self.definir(parametro[1])
                else:
                    self.definir(parametro)
            self.visitar(nodo[-1], locales, ambito_cuerpo)
            self.alcances.pop()
            self.bucles = buclesprevios
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


def probar(archivo, usuario):
    """Analiza un archivo, muestra su resultado y guarda el log de la ejecución."""
    try:
        errores = analizar(archivo.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as error:
        errores = [f"Error al leer el archivo: {error}"]
    resultado = errores or ["Análisis semántico correcto."]
    salida = "\n".join([f"Archivo analizado: {archivo}", *resultado])

    carpeta = Path("logs")
    carpeta.mkdir(exist_ok=True)
    marca = datetime.now().strftime("%d-%m-%Y-%Hh%M")
    nombre = f"semantico-{usuario}-{marca}"
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
    cli.add_argument("-u", "--usuario", required=True,
                     help="usuario de Git (va en el nombre del log)")
    args = cli.parse_args()
    resultados = [probar(archivo, args.usuario) for archivo in args.archivos]
    raise SystemExit(0 if all(resultados) else 1)
