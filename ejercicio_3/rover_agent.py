"""
rover_agent.py
--------------
Agente basado en objetivos que resuelve problemas mediante busqueda
(libro 4a ed. seccion 3.1; Algoritmo "Agente planificador del rover" de
la memoria). Mismo papel que logical_agent.py en el ejercicio 1:

    si no hay plan:
        problema <- FORMULAR(terreno, posicion, objetivo)
        plan     <- BUSCAR(problema)
    accion <- primera accion del plan; plan <- resto

PASO 4 -- pendiente de implementar (y, opcionalmente, replanificacion A3).
"""


class RoverAgent:

    def __init__(self, algoritmo, heuristica=None):
        self.algoritmo = algoritmo
        self.heuristica = heuristica
        self.plan = []

    def formular(self, terreno, posicion, objetivo):
        raise NotImplementedError

    def buscar(self, problema):
        raise NotImplementedError

    def __call__(self, percepcion):
        raise NotImplementedError
