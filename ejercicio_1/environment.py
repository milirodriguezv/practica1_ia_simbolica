"""
Environment
-----------
Representa el problema tal como existe "en el mundo real", fuera del
agente: en este caso, el GRAFO que hay que colorear (regiones y sus
adyacencias), mas los colores disponibles.

El entorno NO sabe nada de logica proposicional, ni de clausulas, ni
de DPLL. Solo conoce conceptos del dominio: regiones, vecinos, colores.

Por eso tiene un metodo "traducir_a_clausulas()": es el puente que
convierte el problema real a lenguaje SAT, para que el agente pueda
anotarlo en su KnowledgeBase. Esa traduccion es un servicio que presta
el entorno, no algo que el entorno "es".
"""

from graph_coloring import crear_variables, generar_clausulas


class Environment:

    def __init__(self, regiones, adyacencias, colores):
        self.regiones = regiones
        self.adyacencias = adyacencias
        self.colores = colores

        # el diccionario de traduccion: que numero de variable le corresponde a cada par (region, color)
        self.variable_id = crear_variables(regiones, colores)

    def traducir_a_clausulas(self):
        """
        Convierte las reglas del grafo (vecinos con distinto color,
        cada region con exactamente un color) a clausulas FNC.
        Esto es lo unico que la KnowledgeBase va a recibir del entorno.
        """
        return generar_clausulas(self.regiones, self.colores,
                                  self.adyacencias, self.variable_id)

    def goal_test(self, asignacion_de_variables):
        """
        Recibe una asignacion de VARIABLES (numeros -> True/False, tal
        como la devuelve el DPLLSolver) y comprueba, desde el propio
        entorno, si esa asignacion corresponde a un coloreado valido
        del grafo: cada region con un color, y ningun par de vecinos
        compartiendo color.
        """
        coloreado = self.decodificar(asignacion_de_variables)

        for region in self.regiones:
            if region not in coloreado:
                return False  # a esta region no se le asigno ningun color

        for region_a, region_b in self.adyacencias:
            if coloreado[region_a] == coloreado[region_b]:
                return False  # dos vecinos con el mismo color

        return True

    def decodificar(self, asignacion_de_variables):
        """Traduce 'variable numero 7 = True' de vuelta a 'SA = Azul'.
        Publico: main.py lo usa para mostrar el resultado en un
        formato legible (nombre de region -> nombre de color)."""
        coloreado = {}
        for region in self.regiones:
            for color in self.colores:
                variable = self.variable_id[(region, color)]
                if asignacion_de_variables.get(variable) is True:
                    coloreado[region] = color
        return coloreado
