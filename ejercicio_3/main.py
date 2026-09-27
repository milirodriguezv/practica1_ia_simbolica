"""
main.py -- Ejercicio 3: agente planificador de rutas para un rover en
Marte, resuelto con A* (busqueda informada).

    parametros.py          -> constantes fisicas del rover (s, v_max, theta_max...)
    terrain.py             -> el entorno: generador de terreno + reglas de movimiento (Terreno)
    problem.py             -> la formulacion como problema de busqueda + coste (RoverProblem)
    heuristics.py          -> h0, h1 (euclidea), h2 (octil), h2 ponderada
    search.py              -> busqueda primero-el-mejor generica: UCS, voraz, A*
    metrics.py             -> factor de ramificacion efectivo b*
    rover_agent.py         -> el ciclo formular -> buscar -> ejecutar (RoverAgent)
    visualizar_terreno.py  -> dibuja mapas y rutas (nada de busqueda aqui)
    run_experiments.py     -> experimentos E1-E5 -> results/*.csv
    make_figures.py        -> figuras de la memoria -> figures/*.pdf

Estado actual: paso 1 (terreno). Genera un mapa, lo guarda y lo dibuja.
"""

from pathlib import Path

from terrain import ParametrosGenerador, generar_terreno, guardar_terreno
from visualizar_terreno import dibujar_terreno

CARPETA_MAPAS = Path(__file__).parent / "maps"


def generar_y_dibujar(N, semilla):
    print(f"--- Terreno {N}x{N}, semilla {semilla} ---")

    params = ParametrosGenerador(N=N)
    terreno = generar_terreno(params, semilla)
    print(terreno.resumen())

    CARPETA_MAPAS.mkdir(exist_ok=True)
    guardar_terreno(terreno, CARPETA_MAPAS / f"terreno_N{N}_s{semilla}.npz", params)

    dibujar_terreno(terreno, f"Terreno sintético {N}x{N} (semilla {semilla})",
                    f"terreno_N{N}_s{semilla}.png")

    # TODO (pasos siguientes):
    #   problema = RoverProblem(terreno)
    #   agente = RoverAgent(algoritmo=astar, heuristica=h2)
    #   rutas = {"UCS": ..., "Voraz": ..., "A* (h1)": ..., "A* (h2)": ...}
    #   dibujar_terreno(terreno, ..., rutas=rutas)
    print()
    return terreno


if __name__ == "__main__":
    generar_y_dibujar(N=100, semilla=0)
    generar_y_dibujar(N=200, semilla=1)
