"""Ejercicio 3: agente planificador de rutas para un rover en Marte.

Resuelto con A* (busqueda informada). Este archivo genera dos mapas, los
guarda, deja que el agente los recorra con UCS, voraz, A*(h1) y A*(h2),
y dibuja las cuatro rutas.

    parametros.py          -> constantes fisicas del rover (s, v_max, theta_max...)
    terrain.py             -> el entorno: generador de terreno + reglas de movimiento (Terreno)
    problem.py             -> la formulacion como problema de busqueda + coste (RoverProblem)
    heuristics.py          -> h0, h1 (euclidea), h2 (octil)
    search.py              -> busqueda primero-el-mejor generica: UCS, voraz, A*
    metrics.py             -> factor de ramificacion efectivo b*
    rover_agent.py         -> el ciclo formular -> buscar -> ejecutar (RoverAgent)
    visualizar_terreno.py  -> dibuja mapas y rutas (nada de busqueda aqui)
    run_experiments.py     -> experimentos -> results/*.csv
    make_figures.py        -> figuras de la memoria -> figures/*.pdf
"""

from pathlib import Path

from heuristics import h1, h2
from rover_agent import RoverAgent
from search import astar_search, greedy_search, uniform_cost_search
from terrain import ParametrosGenerador, generar_terreno, guardar_terreno
from visualizar_terreno import dibujar_rutas_por_separado, dibujar_terreno

CARPETA_MAPAS = Path(__file__).parent / "maps"

AGENTES = {
    "UCS": (uniform_cost_search, None),
    "Voraz (h2)": (greedy_search, h2),
    "A* (h1)": (astar_search, h1),
    "A* (h2)": (astar_search, h2),
}


def simular(agente, terreno, max_pasos=100_000):
    """Bucle agente-entorno: percibir y actuar hasta llegar a G (o no poder).

    Args:
        agente: RoverAgent.
        terreno: Terreno con inicio y objetivo.
        max_pasos: Tope de pasos, por seguridad.

    Returns:
        Lista de celdas por las que ha pasado el rover.
    """
    posicion = terreno.inicio
    recorrido = [posicion]
    for _ in range(max_pasos):
        accion = agente((terreno, posicion, terreno.objetivo))
        if accion is None:
            break
        posicion = (posicion[0] + accion[0], posicion[1] + accion[1])
        recorrido.append(posicion)
    return recorrido


def generar_y_dibujar(N, semilla):
    """Genera un terreno, lo recorre con los cuatro algoritmos y dibuja las rutas.

    Args:
        N: Tamano del mapa (N x N celdas).
        semilla: Semilla del generador de terreno.

    Returns:
        El Terreno generado.
    """
    print(f"--- Terreno {N}x{N}, semilla {semilla} ---")

    params = ParametrosGenerador(N=N)
    terreno = generar_terreno(params, semilla)
    print(terreno.resumen())

    CARPETA_MAPAS.mkdir(exist_ok=True)
    guardar_terreno(terreno, CARPETA_MAPAS / f"terreno_N{N}_s{semilla}.npz", params)

    dibujar_terreno(terreno, f"Terreno sintético {N}x{N} (semilla {semilla})",
                    f"terreno_N{N}_s{semilla}.pdf")

    rutas, expandidos, subtitulos = {}, {}, {}
    print(f"{'algoritmo':<11} {'coste (s)':>10} {'pasos':>6} {'generados':>10} "
          f"{'expandidos':>11} {'tiempo (s)':>11}")
    for nombre, (algoritmo, heuristica) in AGENTES.items():
        agente = RoverAgent(algoritmo, heuristica)
        recorrido = simular(agente, terreno)
        r = agente.resultado
        if recorrido[-1] != terreno.objetivo:
            print(f"{nombre:<11} no llega a G")
            continue
        rutas[nombre] = recorrido
        expandidos[nombre] = r.orden_expansion
        subtitulos[nombre] = f"coste {r.coste:.0f} s · {r.expandidos} expandidos"
        print(f"{nombre:<11} {r.coste:>10.1f} {r.profundidad:>6} {r.generados:>10} "
              f"{r.expandidos:>11} {r.tiempo:>11.3f}")

    dibujar_terreno(terreno, f"Rutas en el terreno {N}x{N} (semilla {semilla})",
                    f"rutas_N{N}_s{semilla}.pdf", rutas=rutas)
    dibujar_rutas_por_separado(terreno, f"Terreno {N}x{N} (semilla {semilla})",
                               f"rutas_paneles_N{N}_s{semilla}.pdf", rutas,
                               expandidos=expandidos, subtitulos=subtitulos)
    print()
    return terreno


if __name__ == "__main__":
    generar_y_dibujar(N=100, semilla=0)
    generar_y_dibujar(N=200, semilla=1)
