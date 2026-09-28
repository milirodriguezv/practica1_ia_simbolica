"""
search.py
---------
Busqueda primero-el-mejor generica en GRAFO (libro 4a ed. seccion 3.3.2,
figura 3.7; basada en best_first_search de aima-python -> citar). Todos
los algoritmos salen del mismo codigo cambiando la funcion de evaluacion,
que aqui se escribe como f(n) = peso_g * g(n) + peso_h * h(n):

                  peso_g  peso_h
    UCS    ->       1       0      f(n) = g(n)
    Voraz  ->       0       1      f(n) = h(n)
    A*     ->       1       1      f(n) = g(n) + h(n)

Detalles que hay que respetar (guia, 6.2):
    - cola de prioridad con heapq, desempate por h menor
    - guardar el mejor g por nodo y descartar entradas obsoletas al sacarlas
    - test objetivo AL EXPANDIR, no al generar
    - contar nodos generados, expandidos, tamano maximo de la frontera, tiempo

"""

import heapq
import time
from dataclasses import dataclass, field

from heuristics import h0


@dataclass
class ResultadoBusqueda:
    ruta: list = None  # lista de celdas de S a G (None si no hay solucion)
    coste: float = float("inf")  # tiempo total [s]
    generados: int = 0
    expandidos: int = 0
    frontera_max: int = 0
    tiempo: float = 0.0  # segundos que tarda el planificador (perf_counter)
    orden_expansion: list = field(default_factory=list)  # para dibujar nodos expandidos

    @property
    def profundidad(self):
        return len(self.ruta) - 1 if self.ruta else None


def best_first_search(problema, h, peso_g=1.0, peso_h=1.0):
    """Busqueda primero-el-mejor con f(n) = peso_g * g(n) + peso_h * h(n).

    Args:
        problema: RoverProblem (initial, actions, result, is_goal, action_cost).
        h: Heuristica h(estado, problema). Ademas de entrar en f, se usa
            para desempatar: a igual f sale antes el nodo de menor h.
        peso_g: Peso del coste ya recorrido g.
        peso_h: Peso de la estimacion h de lo que falta.

    Returns:
        ResultadoBusqueda con la ruta (None si no hay camino), su coste y
        los contadores de nodos generados, expandidos, frontera maxima y
        tiempo.
    """
    time_inicial = time.perf_counter()  # reloj de alta resolucion (process_time va a saltos de ~16 ms en Windows)
    S = problema.initial
    mejor_g = {S: 0}  # mejor coste g encontrado hasta ahora por cada nodo
    padre = {S: None}
    contador = 0
    h_S = h(S, problema)  # Coste estimado por la heuristica desde el nodo inicial
    frontera = [(peso_h * h_S, h_S, contador, 0, S)]  # f(S) = peso_g * 0 + peso_h * h
    generados, expandidos, frontera_max = 1, 0, 0
    orden_expansion = []
    while frontera:
        frontera_max = max(frontera_max, len(frontera))
        _, _, _, g, celda = heapq.heappop(frontera)
        if g > mejor_g[celda]:  # entrada obsoleta, descartar
            continue
        expandidos += 1
        orden_expansion.append(celda)
        if problema.is_goal(celda):  # test objetivo al expandir
            ruta = []
            while celda is not None:
                ruta.append(celda)
                celda = padre[celda]
            ruta.reverse()
            time_final = time.perf_counter() - time_inicial
            return ResultadoBusqueda(
                ruta=ruta,
                coste=g,
                generados=generados,
                expandidos=expandidos,
                frontera_max=frontera_max,
                tiempo=time_final,
                orden_expansion=orden_expansion,
            )
        for accion in problema.actions(celda):
            hijo = problema.result(celda, accion)
            coste = problema.action_cost(celda, accion, hijo)
            g_hijo = g + coste
            if hijo not in mejor_g or g_hijo < mejor_g[hijo]:
                mejor_g[hijo] = g_hijo
                padre[hijo] = celda
                generados += 1
                contador += 1
                h_hijo = h(hijo, problema)
                f_hijo = peso_g * g_hijo + peso_h * h_hijo
                heapq.heappush(frontera, (f_hijo, h_hijo, contador, g_hijo, hijo))

    time_final = time.perf_counter() - time_inicial
    return ResultadoBusqueda(
        ruta=None,
        coste=float("inf"),
        generados=generados,
        expandidos=expandidos,
        frontera_max=frontera_max,
        tiempo=time_final,
        orden_expansion=orden_expansion,
    )


def uniform_cost_search(problema):
    """UCS: f = g. Sin heuristica (h0 = 0, asi que tampoco desempata)."""
    return best_first_search(problema, h0, peso_g=1, peso_h=0)


def greedy_search(problema, h):
    """Voraz: f = h. Ignora el coste ya recorrido; rapida pero no optima."""
    return best_first_search(problema, h, peso_g=0, peso_h=1)


def astar_search(problema, h):
    """A*: f = g + h. Con h admisible es optima; con h consistente, ademas,
    ninguna celda se expande dos veces."""
    return best_first_search(problema, h, peso_g=1, peso_h=1)
