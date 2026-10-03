"""Experimentos del ejercicio 1 sobre los mapas de Australia y EE. UU.

Todos se hacen sobre los dos mapas del ejercicio, no sobre formulas
aleatorias:

    numero_cromatico      El agente pregunta con 2, 3, 4... colores hasta
                          que la respuesta es SAT. El ultimo UNSAT es la
                          prueba de que con menos colores no se puede.

    reglas_de_dpll        Cuanto ayudan la clausula unitaria y el simbolo
                          puro al colorear los mapas: se resuelve cada
                          mapa con las reglas activadas y desactivadas.

    estados_conflictivos  Por que EE. UU. no se puede pintar con 3
                          colores: se buscan los estados "culpables".

    fuerza_bruta          Comprobacion: en Australia, que es pequena, se
                          prueban todas las posibilidades una a una y se
                          compara con lo que responde el agente.

Los resultados se guardan en results/ (CSV) y figures/ (imagenes).
Uso: python experimentos.py      (unos 3 minutos, casi todo en reglas_de_dpll)
"""

import csv
import itertools
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from dpll_solver import DPLLSolver, LimiteSuperado
from environment import Environment
from logical_agent import LogicalAgent
from mapas import AUSTRALIA, EEUU, VECINOS_EEUU
from visualizar_mapa import dibujar_solucion

# la consola de Windows no siempre esta en UTF-8 y hay textos con tildes
sys.stdout.reconfigure(encoding="utf-8")

CARPETA = Path(__file__).parent
CARPETA_RESULTADOS = CARPETA / "results"
CARPETA_FIGURAS = CARPETA / "figures"

MAPAS = {"Australia": AUSTRALIA, "EE. UU.": EEUU}
COLORES = ["Rojo", "Verde", "Azul", "Amarillo"]

# Sin la clausula unitaria DPLL puede tardar horas con el mapa de EE. UU.
# Si pasa de este numero de llamadas se corta y se anota como "no termina".
MAX_LLAMADAS = 600_000


def colorear(regiones, adyacencias, n_colores, solver=None):
    """Lanza el agente sobre un mapa con un numero de colores.

    Args:
        regiones: Lista de regiones del mapa.
        adyacencias: Lista de fronteras (pares de regiones).
        n_colores: Numero de colores disponibles.
        solver: DPLLSolver a usar. Si es None, el del agente por defecto.

    Returns:
        Tupla (hay_solucion, entorno, agente). Las estadisticas del solver
        quedan en agente.solver.estadisticas.
    """
    entorno = Environment(regiones, adyacencias, COLORES[:n_colores])
    agente = LogicalAgent()
    if solver is not None:
        agente.solver = solver
    asignacion = agente.run(entorno)
    return asignacion is not None, entorno, agente


def guardar_csv(filas, nombre):
    """Guarda una lista de filas en results/.

    Args:
        filas: Lista de diccionarios, todos con las mismas claves.
        nombre: Nombre del archivo CSV.
    """
    CARPETA_RESULTADOS.mkdir(exist_ok=True)
    with open(CARPETA_RESULTADOS / nombre, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=list(filas[0]))
        escritor.writeheader()
        escritor.writerows(filas)
    print(f"  guardado results/{nombre}")


# ---------------------------------------------------------------------
#  Numero cromatico de cada mapa
# ---------------------------------------------------------------------

def numero_cromatico():
    """Busca el menor numero de colores con el que se puede pintar cada mapa.

    El agente pregunta con 2, 3, 4... colores hasta que la respuesta es
    SAT. Guarda una fila por pregunta en results/numero_cromatico.csv.
    """
    filas = []
    for nombre, mapa in MAPAS.items():
        n_colores = 2
        while True:
            sat, entorno, agente = colorear(mapa["regiones"], mapa["adyacencias"], n_colores)
            e = agente.solver.estadisticas
            filas.append({
                "mapa": nombre,
                "colores": n_colores,
                "variables": len(entorno.variable_id),
                "clausulas": len(agente.kb.clauses),
                "resultado": "SAT" if sat else "UNSAT",
                "llamadas": e.llamadas,
                "decisiones": e.decisiones,
                "propagaciones": e.propagaciones,
                "retrocesos": e.retrocesos,
                "tiempo_ms": round(e.tiempo * 1000, 2),
            })
            if sat:
                break
            n_colores += 1
        print(f"  {nombre}: hacen falta {n_colores} colores")

    for f in filas:
        print(f"    {f['mapa']:<10} {f['colores']} colores: {f['resultado']:<5} "
              f"({f['variables']} variables, {f['clausulas']} clausulas, "
              f"{f['llamadas']} llamadas, {f['tiempo_ms']} ms)")
    guardar_csv(filas, "numero_cromatico.csv")


# ---------------------------------------------------------------------
#  Efecto de las reglas de DPLL al colorear los mapas
# ---------------------------------------------------------------------

# nombre -> (usar clausula unitaria, usar simbolo puro)
VARIANTES = {
    "DPLL completo": (True, True),
    "sin símbolo puro": (True, False),
    "sin cláusula unitaria": (False, True),
    "solo backtracking": (False, False),
}

# (mapa, numero de colores)
CASOS = [("Australia", 2), ("Australia", 3), ("EE. UU.", 2), ("EE. UU.", 3), ("EE. UU.", 4)]

COLORES_VARIANTES = ["#4f6d8f", "#8fb58f", "#d9735a", "#ecc463"]


def reglas_de_dpll():
    """Resuelve cada caso con las cuatro variantes de DPLL.

    Guarda una fila por caso y variante en results/reglas_dpll.csv y la
    figura figures/reglas_dpll.pdf.
    """
    filas = []
    for nombre, n_colores in CASOS:
        mapa = MAPAS[nombre]
        for variante, (unitaria, puro) in VARIANTES.items():
            solver = DPLLSolver(unitaria, puro, max_llamadas=MAX_LLAMADAS)
            try:
                sat, _, _ = colorear(mapa["regiones"], mapa["adyacencias"], n_colores, solver)
                resultado = "SAT" if sat else "UNSAT"
            except LimiteSuperado:
                resultado = "no termina"

            e = solver.estadisticas
            filas.append({
                "mapa": nombre,
                "colores": n_colores,
                "variante": variante,
                "resultado": resultado,
                "llamadas": e.llamadas,
                "decisiones": e.decisiones,
                "propagaciones": e.propagaciones,
                "simbolos_puros": e.simbolos_puros,
                "tiempo_s": round(e.tiempo, 3),
            })
            print(f"  {nombre} con {n_colores} colores, {variante}: {resultado}, "
                  f"{e.llamadas} llamadas, {e.simbolos_puros} simbolos puros, {e.tiempo:.2f} s")

    guardar_csv(filas, "reglas_dpll.csv")
    figura_reglas_de_dpll(filas)


def figura_reglas_de_dpll(filas):
    """Dibuja las llamadas recursivas de cada variante en cada caso.

    Barras agrupadas: un grupo por caso y una barra por variante. Las
    barras rayadas son las que se han cortado en MAX_LLAMADAS.

    Args:
        filas: Filas generadas por reglas_de_dpll().
    """
    figura, ejes = plt.subplots(figsize=(7.5, 3.8))
    ancho = 0.2

    for i, (variante, color) in enumerate(zip(VARIANTES, COLORES_VARIANTES)):
        for j, (nombre, n_colores) in enumerate(CASOS):
            fila = next(f for f in filas if f["mapa"] == nombre
                        and f["colores"] == n_colores and f["variante"] == variante)
            cortada = fila["resultado"] == "no termina"
            x = j + (i - 1.5) * ancho
            ejes.bar(x, fila["llamadas"], ancho, color=color,
                     hatch="///" if cortada else None, edgecolor="white",
                     label=variante if j == 0 else None)

    ejes.set_yscale("log")
    ejes.set_ylim(top=MAX_LLAMADAS * 40)
    ejes.set_xticks(range(len(CASOS)), [f"{nombre}\n{k} colores" for nombre, k in CASOS])
    ejes.set_ylabel("llamadas recursivas (escala log)")
    ejes.set_title("Colorear los mapas con y sin las reglas de DPLL (rayado: no termina)",
                   fontsize=10)
    ejes.legend(fontsize=8, ncol=4, loc="upper left", frameon=False)
    ejes.spines[["top", "right"]].set_visible(False)

    figura.tight_layout()
    CARPETA_FIGURAS.mkdir(exist_ok=True)
    figura.savefig(CARPETA_FIGURAS / "reglas_dpll.pdf")
    plt.close(figura)
    print("  guardado figures/reglas_dpll.pdf")


# ---------------------------------------------------------------------
#  Que estados impiden pintar EE. UU. con 3 colores
# ---------------------------------------------------------------------

def trozo_de_eeuu(estados):
    """Reduce el mapa de EE. UU. a unos pocos estados.

    Args:
        estados: Estados con los que quedarse.

    Returns:
        Tupla (regiones, fronteras) con esos estados y las fronteras que
        hay entre ellos.
    """
    estados = set(estados)
    fronteras = [(a, b) for a, b in EEUU["adyacencias"] if a in estados and b in estados]
    return sorted(estados), fronteras


def se_puede_con_3_colores(estados):
    """Pregunta al agente si un trozo de EE. UU. admite 3 colores.

    Args:
        estados: Estados que forman el trozo de mapa.

    Returns:
        True si existe un coloreado con 3 colores.
    """
    regiones, fronteras = trozo_de_eeuu(estados)
    sat, _, _ = colorear(regiones, fronteras, 3)
    return sat


def estados_conflictivos():
    """Busca los estados que impiden pintar EE. UU. con 3 colores.

    Guarda results/estados_conflictivos.csv y la figura
    figures/estados_conflictivos.pdf.
    """
    # 1) Un estado es "conflictivo" si el solo con sus vecinos ya no se
    #    puede pintar con 3 colores (pasa cuando lo rodea un numero impar
    #    de estados: el anillo necesita 3 colores y el del centro, un cuarto).
    conflictivos = []
    for estado, vecinos in VECINOS_EEUU.items():
        if not se_puede_con_3_colores([estado] + vecinos):
            conflictivos.append(estado)
            print(f"  {estado} y sus {len(vecinos)} vecinos ({', '.join(vecinos)}) "
                  "no se pueden pintar con 3 colores")

    # 2) Si se quitan esos estados del mapa, ¿bastan 3 colores para el resto?
    resto = [e for e in EEUU["regiones"] if e not in conflictivos]
    basta = se_puede_con_3_colores(resto)
    print(f"  Sin {conflictivos}, el resto del mapa con 3 colores: "
          f"{'SAT' if basta else 'UNSAT'}")

    filas = [{"estado": e,
              "n_vecinos": len(VECINOS_EEUU[e]),
              "conflictivo": e in conflictivos}
             for e in EEUU["regiones"]]
    guardar_csv(filas, "estados_conflictivos.csv")

    CARPETA_FIGURAS.mkdir(exist_ok=True)
    # Figura: los conflictivos en rojo y sus vecinos en amarillo; el resto
    # queda en gris porque no se le asigna color.
    resaltado = {}
    for estado in conflictivos:
        for vecino in VECINOS_EEUU[estado]:
            resaltado[vecino] = "Amarillo"
    for estado in conflictivos:
        resaltado[estado] = "Rojo"
    dibujar_solucion(resaltado, EEUU,
                     "Estados que impiden pintar EE. UU. con 3 colores (rojo) y sus vecinos",
                     CARPETA_FIGURAS / "estados_conflictivos.pdf", tamano=250, margen=2)
    print("  guardado figures/estados_conflictivos.pdf")


# ---------------------------------------------------------------------
#  Comprobacion por fuerza bruta en Australia
# ---------------------------------------------------------------------

def contar_coloreados(mapa, n_colores):
    """Cuenta los coloreados validos probando todas las combinaciones.

    No usa clausulas ni el solver: asigna un color a cada region de todas
    las formas posibles (n_colores ^ regiones) y mira las fronteras.

    Args:
        mapa: Diccionario de mapas.py (regiones, adyacencias).
        n_colores: Numero de colores disponibles.

    Returns:
        Numero de coloreados en los que ninguna frontera une dos regiones
        del mismo color.
    """
    regiones = mapa["regiones"]
    validos = 0
    for colores in itertools.product(range(n_colores), repeat=len(regiones)):
        color_de = dict(zip(regiones, colores))
        if all(color_de[a] != color_de[b] for a, b in mapa["adyacencias"]):
            validos += 1
    return validos


def contar_modelos(clausulas, n_variables):
    """Cuenta las asignaciones que satisfacen la formula probando las 2^n.

    Args:
        clausulas: Lista de clausulas (conjuntos de enteros).
        n_variables: Numero de variables; se numeran de 1 a n.

    Returns:
        Numero de modelos de la formula.
    """
    clausulas = [tuple(c) for c in clausulas]
    modelos = 0
    for valores in itertools.product((False, True), repeat=n_variables):
        if all(any(valores[abs(literal) - 1] == (literal > 0) for literal in clausula)
               for clausula in clausulas):
            modelos += 1
    return modelos


def fuerza_bruta():
    """Compara la respuesta del agente con la fuerza bruta en Australia.

    Para 2 y 3 colores se cuentan los coloreados validos del mapa y los
    modelos de la formula. Si la traduccion a clausulas es correcta los
    dos numeros coinciden, y el agente debe responder SAT exactamente
    cuando son mayores que cero. Guarda results/fuerza_bruta.csv.
    """
    filas = []
    for n_colores in (2, 3):
        sat, entorno, agente = colorear(AUSTRALIA["regiones"], AUSTRALIA["adyacencias"], n_colores)
        n_variables = len(entorno.variable_id)
        coloreados = contar_coloreados(AUSTRALIA, n_colores)
        modelos = contar_modelos(agente.kb.clauses, n_variables)
        filas.append({
            "mapa": "Australia",
            "colores": n_colores,
            "combinaciones_de_colores": n_colores ** len(AUSTRALIA["regiones"]),
            "coloreados_validos": coloreados,
            "variables": n_variables,
            "asignaciones": 2 ** n_variables,
            "modelos_de_la_formula": modelos,
            "agente": "SAT" if sat else "UNSAT",
            "coinciden": coloreados == modelos and sat == (coloreados > 0),
        })
        print(f"  Australia con {n_colores} colores: {coloreados} coloreados validos, "
              f"{modelos} modelos de la formula ({2 ** n_variables} asignaciones probadas), "
              f"el agente dice {'SAT' if sat else 'UNSAT'}")
    guardar_csv(filas, "fuerza_bruta.csv")


if __name__ == "__main__":
    print("--- Numero cromatico ---")
    numero_cromatico()
    print("\n--- Reglas de DPLL sobre los mapas ---")
    reglas_de_dpll()
    print("\n--- Estados conflictivos de EE. UU. ---")
    estados_conflictivos()
    print("\n--- Comprobacion por fuerza bruta (Australia) ---")
    fuerza_bruta()
