"""
search.py
---------
Busqueda primero-el-mejor generica en GRAFO (libro 4a ed. seccion 3.3.2,
figura 3.7; basada en best_first_search de aima-python -> citar). Todos
los algoritmos salen del mismo codigo cambiando la funcion de evaluacion f:

    UCS    -> f(n) = g(n)
    Voraz  -> f(n) = h(n)
    A*     -> f(n) = g(n) + h(n)
    A*_w   -> f(n) = g(n) + w * h(n)

Detalles que hay que respetar (guia, 6.2):
    - cola de prioridad con heapq, desempate por h menor
    - guardar el mejor g por nodo y descartar entradas obsoletas al sacarlas
    - test objetivo AL EXPANDIR, no al generar
    - contar nodos generados, expandidos, tamano maximo de la frontera, tiempo

PASO 3 -- pendiente de implementar.
"""

from dataclasses import dataclass, field


@dataclass
class ResultadoBusqueda:
    ruta: list = None             # lista de celdas de S a G (None si no hay solucion)
    coste: float = float("inf")   # tiempo total [s]
    generados: int = 0
    expandidos: int = 0
    frontera_max: int = 0
    tiempo: float = 0.0           # segundos de CPU del planificador
    orden_expansion: list = field(default_factory=list)  # para dibujar nodos expandidos

    @property
    def profundidad(self):
        return len(self.ruta) - 1 if self.ruta else None


def best_first_search(problema, f, h):
    raise NotImplementedError


def uniform_cost_search(problema):
    raise NotImplementedError


def greedy_search(problema, h):
    raise NotImplementedError


def astar_search(problema, h, w=1.0):
    raise NotImplementedError
