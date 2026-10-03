"""Agente planificador del rover.

Agente basado en objetivos que resuelve problemas mediante busqueda
(libro 4a ed. seccion 3.1; Algoritmo "Agente planificador del rover" de
la memoria). Mismo papel que logical_agent.py en el ejercicio 1:

    si no hay plan:
        problema <- FORMULAR(terreno, posicion, objetivo)
        plan     <- BUSCAR(problema)
    accion <- primera accion del plan; plan <- resto

El agente es quien cruza la frontera entre "el mundo" (Terreno, que solo
sabe de alturas y rocas) y "el razonamiento" (search.py, que solo sabe
de problemas de busqueda): lo hace al FORMULAR.

La percepcion es la tupla (terreno, posicion, objetivo). El agente
guarda donde espera estar despues de cada accion; si la percepcion dice
otra cosa (p.ej. el rover ha patinado), tira el plan y replanifica desde
la posicion real.
"""

from itertools import pairwise

from problem import RoverProblem


class RoverAgent:
    """Agente que formula el problema, busca un plan y lo ejecuta paso a paso."""

    def __init__(self, algoritmo, heuristica=None):
        """
        Args:
            algoritmo: Funcion de search.py: astar_search, greedy_search
                (reciben (problema, h)) o uniform_cost_search (solo problema).
            heuristica: h(estado, problema) de heuristics.py. None para UCS.
        """
        self.algoritmo = algoritmo
        self.heuristica = heuristica
        self.plan = []  # acciones (di, dj) pendientes de ejecutar
        self.posicion_esperada = None  # donde deberia estar tras la ultima accion
        self.resultado = None  # ResultadoBusqueda de la ultima busqueda
        self.busquedas = 0  # cuantas veces ha planificado (1 si nunca replanifica)

    def formular(self, terreno, posicion, objetivo):
        """Traduce la situacion actual a un problema de busqueda.

        Args:
            terreno: Terreno por el que se mueve el rover.
            posicion: Celda (i, j) en la que esta.
            objetivo: Celda (i, j) a la que quiere llegar.

        Returns:
            RoverProblem desde posicion hasta objetivo.
        """
        return RoverProblem(terreno, inicio=posicion, objetivo=objetivo)

    def buscar(self, problema):
        """Llama al algoritmo y convierte la ruta en un plan de acciones.

        Si no hay camino el plan queda vacio.

        Args:
            problema: RoverProblem a resolver.

        Returns:
            Lista de acciones (di, dj) para ir de S a G.
        """
        if self.heuristica is None:
            self.resultado = self.algoritmo(problema)
        else:
            self.resultado = self.algoritmo(problema, self.heuristica)
        self.busquedas += 1

        ruta = self.resultado.ruta or []
        self.plan = [(b[0] - a[0], b[1] - a[1]) for a, b in pairwise(ruta)]
        return self.plan

    def __call__(self, percepcion):
        """Decide la siguiente accion a partir de la percepcion.

        Args:
            percepcion: Tupla (terreno, posicion, objetivo).

        Returns:
            Accion (di, dj), o None si ya esta en el objetivo o no existe
            camino.
        """
        terreno, posicion, objetivo = percepcion
        if posicion == objetivo:
            self.plan = []
            return None

        if posicion != self.posicion_esperada:  # primer paso o se ha desviado
            self.plan = []
        if not self.plan:
            self.buscar(self.formular(terreno, posicion, objetivo))
            if not self.plan:
                return None  # sin solucion

        accion = self.plan.pop(0)
        self.posicion_esperada = (posicion[0] + accion[0], posicion[1] + accion[1])
        return accion
