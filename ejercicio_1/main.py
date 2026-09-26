"""
main.py -- Ejercicio 1: agente logico + SAT solver aplicado a
coloreado de grafos (mapa de Australia).

    environment.py       -> el problema real: el GRAFO (Environment)
    knowledge_base.py     -> la libreta logica del agente (KnowledgeBase)
    dpll_solver.py         -> el algoritmo de inferencia (DPLLSolver)
    logical_agent.py       -> el ciclo TELL/ASK (LogicalAgent)
    graph_coloring.py      -> funciones puras: grafo -> clausulas FNC
    visualizar_mapa.py     -> dibuja el resultado (nada de logica aqui)
"""

from environment import Environment
from logical_agent import LogicalAgent
from visualizar_mapa import dibujar_solucion


REGIONES = ["WA", "NT", "SA", "Q", "NSW", "V", "T"]

ADYACENCIAS = [
    ("WA", "NT"),
    ("WA", "SA"),
    ("NT", "SA"),
    ("NT", "Q"),
    ("SA", "Q"),
    ("SA", "NSW"),
    ("SA", "V"),
    ("Q", "NSW"),
    ("NSW", "V"),
    # T (Tasmania) no tiene vecinos, es una isla
]


def resolver_y_dibujar(colores, etiqueta, nombre_archivo_imagen):
    print(f"--- Mapa de Australia con {etiqueta} ---")

    entorno = Environment(REGIONES, ADYACENCIAS, colores)
    print(f"Variables: {len(entorno.variable_id)}")

    agente = LogicalAgent()
    asignacion = agente.run(entorno)

    if asignacion is None:
        print("Resultado: UNSAT (no existe un coloreado valido)\n")
        dibujar_solucion(None, ADYACENCIAS, f"UNSAT con {etiqueta}", nombre_archivo_imagen)
        return None

    coloreado = entorno.decodificar(asignacion)
    print("Resultado: SAT. Coloreado encontrado:")
    for region in REGIONES:
        print(f"  {region}: {coloreado.get(region)}")
    print()

    dibujar_solucion(coloreado, ADYACENCIAS, f"SAT con {etiqueta}", nombre_archivo_imagen)
    return coloreado


if __name__ == "__main__":
    resolver_y_dibujar(["Rojo", "Verde", "Azul"], "3 colores", "mapa_3_colores.png")
    resolver_y_dibujar(["Rojo", "Verde"], "2 colores", "mapa_2_colores.png")
