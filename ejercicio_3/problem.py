"""
problem.py
----------
Formulacion del problema de busqueda (memoria, "Formulacion del
problema de busqueda" y "Modelo de coste"), con la misma interfaz que
la clase Problem del libro y de aima-python:

    estados            -> celdas transitables (i, j)
    estado inicial     -> terreno.inicio
    acciones           -> (di, dj) factibles (las decide terrain.py)
    modelo transicion  -> result((i, j), (di, dj)) = (i + di, j + dj)
    test objetivo      -> estado == terreno.objetivo
    coste de accion    -> c(a, b) = d(a, b) / v(theta(a, b))   [s]

El terreno dice QUE movimientos se pueden hacer; este archivo dice
CUANTO CUESTA (en segundos) cada uno. Aqui aparece la asimetria:
subir cuesta mas que bajar.
"""

import math

from parametros import V_MAX, THETA_MAX, K_SUB, K_BAJ


def velocidad(theta):
    """v(theta) lineal por tramos (ecuacion de la velocidad en la memoria):
        subida (theta >= 0): baja hasta 0.2 * V_MAX en THETA_MAX
        bajada (theta < 0):  baja hasta 0.6 * V_MAX en -THETA_MAX
    Nunca supera V_MAX (Lema 1), que es lo que hace admisibles h1 y h2."""
    if theta >= 0:
        return V_MAX * (1 - K_SUB * theta / THETA_MAX)
    return V_MAX * (1 - K_BAJ * -theta / THETA_MAX)


class RoverProblem:

    def __init__(self, terreno, inicio=None, objetivo=None):
        self.terreno = terreno
        self.initial = inicio if inicio is not None else terreno.inicio
        self.goal = objetivo if objetivo is not None else terreno.objetivo

    def actions(self, estado):
        return self.terreno.movimientos_factibles(estado)

    def result(self, estado, accion):
        return (estado[0] + accion[0], estado[1] + accion[1])

    def is_goal(self, estado):
        return estado == self.goal

    def action_cost(self, estado, accion, siguiente):
        """Tiempo [s] del paso estado -> siguiente: distancia recorrida
        (con la cuesta incluida) entre la velocidad a esa pendiente."""
        d_h = self.terreno.distancia_horizontal(*accion)
        desnivel = self.terreno.alturas[siguiente] - self.terreno.alturas[estado]
        theta = self.terreno.pendiente(estado, siguiente)
        return math.hypot(d_h, desnivel) / velocidad(theta)
