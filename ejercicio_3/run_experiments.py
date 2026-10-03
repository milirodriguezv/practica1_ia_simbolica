"""Experimentos del ejercicio 3.

Cada uno escribe un CSV en results/ (una fila por busqueda):

    heuristicas       UCS, A*(h1) y A*(h2) sobre muchos objetivos: nodos
                      generados, expandidos y b* frente a la profundidad d
    voraz             busqueda voraz frente a A*: cuanto tiempo de viaje
                      pierde el rover y cuantos nodos se ahorra al planificar
    ida_y_vuelta      coste de ir de S a G frente a volver de G a S
                      (subir cuesta mas que bajar)
    pendiente_maxima  que pasa si el rover aguanta menos pendiente: si
                      sigue habiendo ruta y cuanto se alarga el viaje
    referencia        comprobacion: coste de UCS, A*(h1) y A*(h2) frente al
                      Dijkstra de networkx sobre el mismo grafo

Dos tipos de terreno ("base" y "abrupto", ver params_para) para que haya
variedad de pendientes. Todo depende de semillas fijas: volver a ejecutar
da los mismos CSV (salvo la columna de tiempo).

Uso:
    python run_experiments.py                     # todos (unos minutos)
    python run_experiments.py voraz ida_y_vuelta  # solo algunos
    python run_experiments.py --rapido            # pocos mapas, para probar
"""

import argparse
import csv
import math
import time
from pathlib import Path

import networkx as nx
import numpy as np

from heuristics import h1, h2
from metrics import b_estrella
from problem import RoverProblem
from search import astar_search, greedy_search, uniform_cost_search
from terrain import ParametrosGenerador, Terreno, generar_terreno

CARPETA_RESULTADOS = Path(__file__).parent / "results"

TIPOS_TERRENO = ["base", "abrupto"]
N = 100  # tamano de los mapas (N x N celdas de 1 m)

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

# Pendientes maximas que se prueban en pendiente_maxima [grados].
# 25 es la del rover del ejercicio (parametros.THETA_MAX).
PENDIENTES_MAXIMAS = [10, 15, 20, 25]


# ---------------------------------------------------------------------
#  Utilidades comunes
# ---------------------------------------------------------------------


def params_para(tipo="base"):
    """Devuelve los parametros del generador para un tipo de terreno.

    base:    los valores por defecto, con 3 crateres en el mapa de 100 x 100.
    abrupto: el doble de crateres y un relieve base 3 veces mas alto
             (pendientes de hasta ~15-20 grados fuera de los crateres).

    Args:
        tipo: "base" o "abrupto".

    Returns:
        ParametrosGenerador.

    Raises:
        ValueError: Si el tipo no es ninguno de los dos.
    """
    n_crateres = max(1, round(12 * (N / 200) ** 2))
    if tipo == "base":
        return ParametrosGenerador(N=N, n_crateres=n_crateres)
    if tipo == "abrupto":
        return ParametrosGenerador(N=N, n_crateres=2 * n_crateres, amplitud_base=3.0)
    raise ValueError(f"Tipo de terreno desconocido: {tipo}")


def fila_resultado(r):
    """Extrae las columnas comunes de un resultado de busqueda.

    Args:
        r: ResultadoBusqueda.

    Returns:
        Diccionario con coste, d, generados, expandidos, frontera_max,
        b_estrella y tiempo.
    """
    return {
        "coste": r.coste,
        "d": r.profundidad,
        "generados": r.generados,
        "expandidos": r.expandidos,
        "frontera_max": r.frontera_max,
        "b_estrella": b_estrella(r),
        "tiempo": r.tiempo,
    }


def objetivos_aleatorios(terreno, rng, k):
    """Elige objetivos al azar entre las celdas alcanzables desde S.

    Al ser al azar, las distancias (y por tanto d) quedan repartidas entre
    casi 0 y la diagonal del mapa.

    Args:
        terreno: Terreno con inicio.
        rng: Generador aleatorio de numpy.
        k: Numero de objetivos.

    Returns:
        Lista de hasta k celdas (i, j) distintas.
    """
    alcanzables = terreno.alcanzables_desde(terreno.inicio)
    alcanzables[terreno.inicio] = False
    celdas = np.argwhere(alcanzables)
    elegidas = rng.choice(len(celdas), size=min(k, len(celdas)), replace=False)
    return [tuple(int(x) for x in celdas[e]) for e in elegidas]


def guardar_csv(filas, nombre):
    """Guarda una lista de filas en results/.

    Args:
        filas: Lista de diccionarios, todos con las mismas claves.
        nombre: Nombre del archivo CSV.
    """
    CARPETA_RESULTADOS.mkdir(exist_ok=True)
    ruta = CARPETA_RESULTADOS / nombre
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        escritor.writeheader()
        escritor.writerows(filas)
    print(f"  -> {ruta} ({len(filas)} filas)")


def progreso(texto, actual, total):
    """Muestra el avance de un experimento en la misma linea.

    Args:
        texto: Descripcion de lo que se esta haciendo.
        actual: Mapas ya procesados.
        total: Mapas totales.
    """
    print(f"\r  {texto}: {actual}/{total}", end="" if actual < total else "\n", flush=True)


# ---------------------------------------------------------------------
#  Experimentos
# ---------------------------------------------------------------------


def heuristicas(n_mapas, objetivos_por_mapa):
    """Compara UCS, A*(h1) y A*(h2) sobre muchos pares (S, G) con d variado.

    Args:
        n_mapas: Mapas por tipo de terreno.
        objetivos_por_mapa: Objetivos aleatorios que se prueban en cada mapa.
    """
    filas = []
    for tipo in TIPOS_TERRENO:
        for k in range(n_mapas):
            semilla = 2000 + k
            terreno = generar_terreno(params_para(tipo), semilla)
            rng = np.random.default_rng(semilla)
            for objetivo in objetivos_aleatorios(terreno, rng, objetivos_por_mapa):
                problema = RoverProblem(terreno, objetivo=objetivo)
                for nombre, algoritmo in OPTIMOS.items():
                    filas.append({"terreno": tipo, "semilla": semilla,
                                  "objetivo": objetivo, "algoritmo": nombre,
                                  **fila_resultado(algoritmo(problema))})
            progreso(f"heuristicas, terreno {tipo}", k + 1, n_mapas)
    guardar_csv(filas, "heuristicas.csv")


def voraz(n_mapas):
    """Compara la voraz (h1 y h2) con el optimo de A*(h2) en el mismo mapa.

    Args:
        n_mapas: Mapas por tipo de terreno.
    """
    filas = []
    for tipo in TIPOS_TERRENO:
        for k in range(n_mapas):
            semilla = 3000 + k
            terreno = generar_terreno(params_para(tipo), semilla)
            problema = RoverProblem(terreno)
            optimo = astar_search(problema, h2)
            for nombre, algoritmo in {"A* (h2)": None, **VORACES}.items():
                r = optimo if algoritmo is None else algoritmo(problema)
                filas.append({"terreno": tipo, "semilla": semilla, "algoritmo": nombre,
                              **fila_resultado(r),
                              "coste_optimo": optimo.coste,
                              "sobrecoste_pct": 100 * (r.coste / optimo.coste - 1),
                              "expandidos_optimo": optimo.expandidos})
            progreso(f"voraz, terreno {tipo}", k + 1, n_mapas)
    guardar_csv(filas, "voraz.csv")


def ida_y_vuelta(n_mapas):
    """Compara el coste optimo de ida (S -> G) y de vuelta (G -> S).

    Args:
        n_mapas: Mapas por tipo de terreno.
    """
    filas = []
    for tipo in TIPOS_TERRENO:
        for k in range(n_mapas):
            semilla = 4000 + k
            terreno = generar_terreno(params_para(tipo), semilla)
            S, G = terreno.inicio, terreno.objetivo
            ida = astar_search(RoverProblem(terreno, S, G), h2)
            vuelta = astar_search(RoverProblem(terreno, G, S), h2)
            filas.append({
                "terreno": tipo, "semilla": semilla,
                "desnivel_SG": float(terreno.alturas[G] - terreno.alturas[S]),  # > 0: G mas alto
                "coste_ida": ida.coste, "coste_vuelta": vuelta.coste,
                "diferencia_pct": 100 * (ida.coste / vuelta.coste - 1),
                "misma_ruta": ida.ruta == vuelta.ruta[::-1],
                "d_ida": ida.profundidad, "d_vuelta": vuelta.profundidad,
            })
            progreso(f"ida y vuelta, terreno {tipo}", k + 1, n_mapas)
    guardar_csv(filas, "ida_y_vuelta.csv")


def pendiente_maxima(n_mapas):
    """Repite la busqueda con rovers que aguantan menos pendiente.

    El mismo mapa, con el mismo S y G, para rovers que aguantan cada vez
    menos pendiente. Con menos pendiente permitida hay mas paredes de
    crater que no se pueden cruzar: la ruta se alarga o deja de existir.
    La referencia es la ruta del rover del ejercicio (25 grados).

    Args:
        n_mapas: Mapas por tipo de terreno.
    """
    filas = []
    for tipo in TIPOS_TERRENO:
        for k in range(n_mapas):
            semilla = 5000 + k
            original = generar_terreno(params_para(tipo), semilla)
            referencia = astar_search(RoverProblem(original), h2)

            for grados in PENDIENTES_MAXIMAS:
                # mismo relieve, mismas rocas, mismo S y G; solo cambia el limite
                terreno = Terreno(original.alturas, original.rocas,
                                  theta_max=math.radians(grados),
                                  inicio=original.inicio, objetivo=original.objetivo)
                r = astar_search(RoverProblem(terreno), h2)
                hay_ruta = r.ruta is not None
                filas.append({
                    "terreno": tipo, "semilla": semilla, "theta_max_grados": grados,
                    "hay_ruta": hay_ruta,
                    "coste": r.coste if hay_ruta else "",
                    "pasos": r.profundidad if hay_ruta else "",
                    "tiempo_extra_pct": 100 * (r.coste / referencia.coste - 1) if hay_ruta else "",
                    "expandidos": r.expandidos,
                })
            progreso(f"pendiente maxima, terreno {tipo}", k + 1, n_mapas)
    guardar_csv(filas, "pendiente_maxima.csv")


def coste_networkx(problema):
    """Calcula el coste optimo de S a G con el Dijkstra de networkx.

    Construye el grafo dirigido de todos los movimientos factibles del
    terreno, con el tiempo de cada paso como peso. No usa search.py, asi
    que sirve de referencia independiente.

    Args:
        problema: RoverProblem.

    Returns:
        Coste del camino mas corto de problema.initial a problema.goal.
    """
    grafo = nx.DiGraph()
    terreno = problema.terreno
    for i in range(terreno.N):
        for j in range(terreno.N):
            for accion in problema.actions((i, j)):
                hijo = problema.result((i, j), accion)
                grafo.add_edge((i, j), hijo, weight=problema.action_cost((i, j), accion, hijo))
    return nx.dijkstra_path_length(grafo, problema.initial, problema.goal)


def referencia(n_mapas):
    """Compara el coste de los tres algoritmos optimos con el de networkx.

    Usa los mismos mapas que el experimento voraz.

    Args:
        n_mapas: Mapas por tipo de terreno.
    """
    filas = []
    for tipo in TIPOS_TERRENO:
        for k in range(n_mapas):
            semilla = 3000 + k
            terreno = generar_terreno(params_para(tipo), semilla)
            problema = RoverProblem(terreno)
            coste_referencia = coste_networkx(problema)
            for nombre, algoritmo in OPTIMOS.items():
                r = algoritmo(problema)
                filas.append({
                    "terreno": tipo, "semilla": semilla, "algoritmo": nombre,
                    "coste": r.coste, "coste_networkx": coste_referencia,
                    "error_relativo": abs(r.coste - coste_referencia) / coste_referencia,
                })
            progreso(f"referencia, terreno {tipo}", k + 1, n_mapas)
    guardar_csv(filas, "referencia_networkx.csv")
    peor = max(f["error_relativo"] for f in filas)
    print(f"  error relativo maximo frente a networkx: {peor:.2e}")


# ---------------------------------------------------------------------


def main():
    """Lee los argumentos y ejecuta los experimentos pedidos."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("experimentos", nargs="*",
                        default=["heuristicas", "voraz", "ida_y_vuelta", "pendiente_maxima",
                                 "referencia"],
                        help="cuales ejecutar (por defecto, todos)")
    parser.add_argument("--rapido", action="store_true", help="pocos mapas, para probar el script")
    args = parser.parse_args()

    n = 3 if args.rapido else 30  # mapas por tipo de terreno
    ejecutar = {
        "heuristicas": lambda: heuristicas(n, objetivos_por_mapa=2 if args.rapido else 8),
        "voraz": lambda: voraz(n),
        "ida_y_vuelta": lambda: ida_y_vuelta(n),
        "pendiente_maxima": lambda: pendiente_maxima(n),
        "referencia": lambda: referencia(n),
    }
    for nombre in args.experimentos:
        print(f"--- {nombre} ---")
        inicio = time.perf_counter()
        ejecutar[nombre]()
        print(f"  ({time.perf_counter() - inicio:.0f} s)")


if __name__ == "__main__":
    main()
