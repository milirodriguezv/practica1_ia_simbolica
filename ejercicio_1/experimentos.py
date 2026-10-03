"""
experimentos.py
---------------
Experimentos del ejercicio 1. Todos se hacen sobre los dos mapas del
ejercicio (Australia y EE. UU.), no sobre formulas aleatorias:

    numero_cromatico      El agente pregunta con 2, 3, 4... colores hasta
                          que la respuesta es SAT. El ultimo UNSAT es la
                          prueba de que con menos colores no se puede.

    reglas_de_dpll        Cuanto ayudan la clausula unitaria y el simbolo
                          puro al colorear los mapas: se resuelve cada
                          mapa con las reglas activadas y desactivadas.

    estados_conflictivos  Por que EE. UU. no se puede pintar con 3
                          colores: se buscan los estados "culpables".

Los resultados se guardan en results/ (CSV) y figures/ (imagenes).
Uso: python experimentos.py      (unos 3 minutos, casi todo en reglas_de_dpll)
"""

import csv
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
    """Lanza el agente sobre un mapa con n_colores.

    Devuelve (hay_solucion, entorno, agente). Las estadisticas del solver
    quedan en agente.solver.estadisticas.
    """
    entorno = Environment(regiones, adyacencias, COLORES[:n_colores])
    agente = LogicalAgent()
    if solver is not None:
        agente.solver = solver
    asignacion = agente.run(entorno)
    return asignacion is not None, entorno, agente


def guardar_csv(filas, nombre):
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
    """Barras agrupadas: un grupo por caso y una barra por variante.
    Las barras rayadas son las que se han cortado en MAX_LLAMADAS."""
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
    """El mapa de EE. UU. reducido a unos pocos estados: devuelve sus
    regiones y las fronteras que hay entre ellos."""
    estados = set(estados)
    fronteras = [(a, b) for a, b in EEUU["adyacencias"] if a in estados and b in estados]
    return sorted(estados), fronteras


def se_puede_con_3_colores(estados):
    regiones, fronteras = trozo_de_eeuu(estados)
    sat, _, _ = colorear(regiones, fronteras, 3)
    return sat


def estados_conflictivos():
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


if __name__ == "__main__":
    print("--- Numero cromatico ---")
    numero_cromatico()
    print("\n--- Reglas de DPLL sobre los mapas ---")
    reglas_de_dpll()
    print("\n--- Estados conflictivos de EE. UU. ---")
    estados_conflictivos()
