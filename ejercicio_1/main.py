"""
main.py -- Ejercicio 1: agente logico + SAT solver aplicado a
coloreado de grafos (mapas de Australia y de EE. UU.).

    mapas.py               -> los datos: regiones, fronteras y posiciones
    environment.py         -> el problema real: el GRAFO (Environment)
    knowledge_base.py      -> la libreta logica del agente (KnowledgeBase)
    dpll_solver.py         -> el algoritmo de inferencia (DPLLSolver)
    logical_agent.py       -> el ciclo TELL/ASK (LogicalAgent)
    graph_coloring.py      -> funciones puras: grafo -> clausulas FNC
    visualizar_mapa.py     -> dibuja el resultado (nada de logica aqui)
"""

from environment import Environment
from logical_agent import LogicalAgent
from mapas import AUSTRALIA, EEUU
from visualizar_mapa import dibujar_solucion

COLORES = ["Rojo", "Verde", "Azul", "Amarillo"]


def resolver_y_dibujar(nombre, mapa, n_colores, nombre_archivo_imagen, **dibujo):
    colores = COLORES[:n_colores]
    print(f"--- {nombre} con {n_colores} colores ---")

    entorno = Environment(mapa["regiones"], mapa["adyacencias"], colores)
    agente = LogicalAgent()
    asignacion = agente.run(entorno)

    e = agente.solver.estadisticas
    print(f"Variables: {len(entorno.variable_id)}, clausulas: {len(agente.kb.clauses)}")
    print(f"DPLL: {e.decisiones} decisiones, {e.propagaciones} propagaciones, "
          f"{e.simbolos_puros} simbolos puros, {e.retrocesos} retrocesos, "
          f"{e.tiempo * 1000:.1f} ms")

    if asignacion is None:
        print("Resultado: UNSAT (no existe un coloreado valido)\n")
        dibujar_solucion(None, mapa, f"{nombre}: UNSAT con {n_colores} colores",
                         nombre_archivo_imagen, **dibujo)
        return None

    coloreado = entorno.decodificar(asignacion)
    print("Resultado: SAT. Coloreado encontrado:")
    print("  " + ", ".join(f"{r}={coloreado[r]}" for r in mapa["regiones"]))
    print()

    dibujar_solucion(coloreado, mapa, f"{nombre}: SAT con {n_colores} colores",
                     nombre_archivo_imagen, **dibujo)
    return coloreado


if __name__ == "__main__":
    resolver_y_dibujar("Australia", AUSTRALIA, 3, "mapa_3_colores.png")
    resolver_y_dibujar("Australia", AUSTRALIA, 2, "mapa_2_colores.png")
    resolver_y_dibujar("EE. UU.", EEUU, 3, "eeuu_3_colores.png", tamano=250, margen=2)
    resolver_y_dibujar("EE. UU.", EEUU, 4, "eeuu_4_colores.png", tamano=250, margen=2)
