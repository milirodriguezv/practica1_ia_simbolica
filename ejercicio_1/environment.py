"""Entorno del ejercicio: el mapa que hay que colorear.

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
    """Mapa a colorear: regiones, fronteras y colores disponibles."""

    def __init__(self, regiones, adyacencias, colores):
        """Crea el entorno.

        Args:
            regiones: Lista de nombres de region.
            adyacencias: Lista de pares (region_a, region_b) que comparten
                frontera.
            colores: Lista de nombres de color disponibles.
        """
        self.regiones = regiones
        self.adyacencias = adyacencias
        self.colores = colores

        # el diccionario de traduccion: que numero de variable le corresponde a cada par (region, color)
        self.variable_id = crear_variables(regiones, colores)

    def traducir_a_clausulas(self):
        """Convierte las reglas del mapa a clausulas FNC.

        Las reglas son: cada region tiene exactamente un color y dos vecinas
        no comparten color. Esto es lo unico que la KnowledgeBase recibe del
        entorno.

        Returns:
            Lista de clausulas (conjuntos de enteros).
        """
        return generar_clausulas(self.regiones, self.colores,
                                  self.adyacencias, self.variable_id)

    def goal_test(self, asignacion_de_variables):
        """Comprueba si una asignacion es un coloreado valido del mapa.

        Args:
            asignacion_de_variables: Diccionario variable -> bool, tal como lo
                devuelve el DPLLSolver.

        Returns:
            True si cada region tiene un color y ningun par de vecinas
            comparte color.
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
        """Traduce una asignacion de variables a un coloreado legible.

        Por ejemplo, "variable 7 = True" pasa a ser "SA = Azul".

        Args:
            asignacion_de_variables: Diccionario variable -> bool.

        Returns:
            Diccionario region -> nombre de color.
        """
        coloreado = {}
        for region in self.regiones:
            for color in self.colores:
                variable = self.variable_id[(region, color)]
                if asignacion_de_variables.get(variable) is True:
                    coloreado[region] = color
        return coloreado
