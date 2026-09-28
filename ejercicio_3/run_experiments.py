"""
run_experiments.py
------------------
Experimentos de la seccion de Resultados (guia, seccion 7). Cada uno
escribe un CSV en results/ (una fila por busqueda):

    E1  correccion: coste A*(h1) = A*(h2) = UCS = networkx (Dijkstra)
    E2  heuristicas: nodos generados, expandidos y b* frente a la profundidad d
    E3  voraz frente a A*: sobrecoste (%) y nodos ahorrados
    E4  asimetria: coste de S -> G frente a G -> S
    E5  escalabilidad: N = 50, 100, 200, 400

Dos tipos de terreno ("base" y "abrupto", ver params_para) para que haya
variedad de pendientes. El numero de crateres crece con N^2, asi la
densidad de crateres es la misma en todos los tamanos. Todo depende de
semillas fijas: volver a ejecutar da los mismos CSV (salvo la columna
de tiempo).

Uso:
    python run_experiments.py              # todos, configuracion completa
    python run_experiments.py E2 E4        # solo algunos
    python run_experiments.py --rapido     # pocos mapas, para probar
"""

import argparse
import csv
import time
from pathlib import Path

import networkx as nx
import numpy as np

from heuristics import h1, h2
from metrics import b_estrella
from problem import RoverProblem
from search import astar_search, greedy_search, uniform_cost_search
from terrain import ParametrosGenerador, generar_terreno

CARPETA_RESULTADOS = Path(__file__).parent / "results"

TIPOS_TERRENO = ["base", "abrupto"]

# Algoritmos: nombre -> funcion(problema) -> ResultadoBusqueda
OPTIMOS = {
    "UCS": uniform_cost_search,
    "A* (h1)": lambda p: astar_search(p, h1),
    "A* (h2)": lambda p: astar_search(p, h2),
}
VORACES = {
    "Voraz (h1)": lambda p: greedy_search(p, h1),
    "Voraz (h2)": lambda p: greedy_search(p, h2),
}


# ---------------------------------------------------------------------
#  Utilidades comunes
# ---------------------------------------------------------------------


def params_para(N, tipo="base"):
    """Parametros del generador para un tamano y un tipo de terreno.

    base:    los valores por defecto, con 12 crateres por cada 200 x 200.
    abrupto: el doble de crateres y un relieve base 3 veces mas alto
             (pendientes de hasta ~15-20 grados fuera de los crateres).
    """
    n_crateres = max(1, round(12 * (N / 200) ** 2))
    if tipo == "base":
        return ParametrosGenerador(N=N, n_crateres=n_crateres)
    if tipo == "abrupto":
        return ParametrosGenerador(N=N, n_crateres=2 * n_crateres, amplitud_base=3.0)
    raise ValueError(f"Tipo de terreno desconocido: {tipo}")


def fila_resultado(r):
    """Columnas comunes de un ResultadoBusqueda."""
    return {
        "coste": r.coste,
        "d": r.profundidad,
        "generados": r.generados,
        "expandidos": r.expandidos,
        "frontera_max": r.frontera_max,
        "b_estrella": b_estrella(r),
        "tiempo": r.tiempo,
    }


def coste_networkx(problema):
    """Coste optimo con Dijkstra de networkx sobre el mismo grafo de
    movimientos: referencia independiente de search.py."""
    grafo = nx.DiGraph()
    t = problema.terreno
    for i in range(t.N):
        for j in range(t.N):
            for accion in problema.actions((i, j)):
                hijo = problema.result((i, j), accion)
                grafo.add_edge((i, j), hijo, weight=problema.action_cost((i, j), accion, hijo))
    return nx.dijkstra_path_length(grafo, problema.initial, problema.goal)


def objetivos_aleatorios(terreno, rng, k):
    """k objetivos distintos elegidos al azar entre las celdas alcanzables
    desde S. Al ser al azar, las distancias (y por tanto d) quedan
    repartidas entre casi 0 y la diagonal del mapa."""
    alcanzables = terreno.alcanzables_desde(terreno.inicio)
    alcanzables[terreno.inicio] = False
    celdas = np.argwhere(alcanzables)
    elegidas = rng.choice(len(celdas), size=min(k, len(celdas)), replace=False)
    return [tuple(int(x) for x in celdas[e]) for e in elegidas]


def guardar_csv(filas, nombre):
    CARPETA_RESULTADOS.mkdir(exist_ok=True)
    ruta = CARPETA_RESULTADOS / nombre
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        escritor.writeheader()
        escritor.writerows(filas)
    print(f"  -> {ruta} ({len(filas)} filas)")


def progreso(texto, actual, total):
    print(f"\r  {texto}: {actual}/{total}", end="" if actual < total else "\n", flush=True)


# ---------------------------------------------------------------------
#  Experimentos
# ---------------------------------------------------------------------


def e1_correccion(n_mapas, N=100):
    """Los tres algoritmos optimos dan el mismo coste que Dijkstra."""
    filas = []
    for tipo in TIPOS_TERRENO:
        for k in range(n_mapas):
            semilla = 1000 + k
            terreno = generar_terreno(params_para(N, tipo), semilla)
            problema = RoverProblem(terreno)
            referencia = coste_networkx(problema)
            for nombre, algoritmo in OPTIMOS.items():
                r = algoritmo(problema)
                filas.append({
                    "terreno": tipo, "N": N, "semilla": semilla, "algoritmo": nombre,
                    "coste": r.coste, "coste_networkx": referencia,
                    "error_relativo": abs(r.coste - referencia) / referencia,
                })
            progreso(f"E1 {tipo}", k + 1, n_mapas)
    guardar_csv(filas, "e1_correccion.csv")
    peor = max(f["error_relativo"] for f in filas)
    print(f"  error relativo maximo frente a networkx: {peor:.2e}")


def e2_heuristicas(n_mapas, objetivos_por_mapa, N=100):
    """UCS, A*(h1) y A*(h2) sobre muchos pares (S, G) con d variado."""
    filas = []
    for tipo in TIPOS_TERRENO:
        for k in range(n_mapas):
            semilla = 2000 + k
            terreno = generar_terreno(params_para(N, tipo), semilla)
            rng = np.random.default_rng(semilla)
            for objetivo in objetivos_aleatorios(terreno, rng, objetivos_por_mapa):
                problema = RoverProblem(terreno, objetivo=objetivo)
                for nombre, algoritmo in OPTIMOS.items():
                    filas.append({"terreno": tipo, "N": N, "semilla": semilla,
                                  "objetivo": objetivo, "algoritmo": nombre,
                                  **fila_resultado(algoritmo(problema))})
            progreso(f"E2 {tipo}", k + 1, n_mapas)
    guardar_csv(filas, "e2_heuristicas.csv")


def e3_voraz(n_mapas, N=100):
    """Voraz (h1 y h2) frente al optimo de A*(h2) en el mismo mapa."""
    filas = []
    for tipo in TIPOS_TERRENO:
        for k in range(n_mapas):
            semilla = 3000 + k
            terreno = generar_terreno(params_para(N, tipo), semilla)
            problema = RoverProblem(terreno)
            optimo = astar_search(problema, h2)
            for nombre, algoritmo in {"A* (h2)": None, **VORACES}.items():
                r = optimo if algoritmo is None else algoritmo(problema)
                filas.append({"terreno": tipo, "N": N, "semilla": semilla, "algoritmo": nombre,
                              **fila_resultado(r),
                              "coste_optimo": optimo.coste,
                              "sobrecoste_pct": 100 * (r.coste / optimo.coste - 1),
                              "expandidos_optimo": optimo.expandidos})
            progreso(f"E3 {tipo}", k + 1, n_mapas)
    guardar_csv(filas, "e3_voraz.csv")


def e4_asimetria(n_mapas, N=100):
    """Coste optimo de ida (S -> G) y de vuelta (G -> S) con A*(h2)."""
    filas = []
    for tipo in TIPOS_TERRENO:
        for k in range(n_mapas):
            semilla = 4000 + k
            terreno = generar_terreno(params_para(N, tipo), semilla)
            S, G = terreno.inicio, terreno.objetivo
            ida = astar_search(RoverProblem(terreno, S, G), h2)
            vuelta = astar_search(RoverProblem(terreno, G, S), h2)
            filas.append({
                "terreno": tipo, "N": N, "semilla": semilla,
                "desnivel_SG": float(terreno.alturas[G] - terreno.alturas[S]),  # > 0: G mas alto
                "coste_ida": ida.coste, "coste_vuelta": vuelta.coste,
                "diferencia_pct": 100 * (ida.coste / vuelta.coste - 1),
                "misma_ruta": ida.ruta == vuelta.ruta[::-1],
                "d_ida": ida.profundidad, "d_vuelta": vuelta.profundidad,
            })
            progreso(f"E4 {tipo}", k + 1, n_mapas)
    guardar_csv(filas, "e4_asimetria.csv")


def e5_escalabilidad(n_mapas, tamanos=(50, 100, 200, 400)):
    """Tiempo, nodos y memoria (frontera maxima) al crecer N. Solo
    terreno base: aqui interesa el tamano, no el relieve."""
    algoritmos = {**OPTIMOS, "Voraz (h2)": VORACES["Voraz (h2)"]}
    filas = []
    for N in tamanos:
        for k in range(n_mapas):
            semilla = 5000 + k
            terreno = generar_terreno(params_para(N), semilla)
            problema = RoverProblem(terreno)
            for nombre, algoritmo in algoritmos.items():
                filas.append({"terreno": "base", "N": N, "semilla": semilla, "algoritmo": nombre,
                              **fila_resultado(algoritmo(problema))})
            progreso(f"E5 N={N}", k + 1, n_mapas)
    guardar_csv(filas, "e5_escalabilidad.csv")


# ---------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("experimentos", nargs="*", default=["E1", "E2", "E3", "E4", "E5"],
                        help="cuales ejecutar (por defecto, todos)")
    parser.add_argument("--rapido", action="store_true", help="pocos mapas, para probar el script")
    args = parser.parse_args()

    n = 3 if args.rapido else 30  # mapas por configuracion
    ejecutar = {
        "E1": lambda: e1_correccion(n),
        "E2": lambda: e2_heuristicas(n, objetivos_por_mapa=2 if args.rapido else 8),
        "E3": lambda: e3_voraz(n),
        "E4": lambda: e4_asimetria(n),
        "E5": lambda: e5_escalabilidad(2 if args.rapido else 20),
    }
    for nombre in args.experimentos:
        nombre = nombre.upper()
        print(f"--- {nombre} ---")
        inicio = time.perf_counter()
        ejecutar[nombre]()
        print(f"  ({time.perf_counter() - inicio:.0f} s)")


if __name__ == "__main__":
    main()
