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

from parametros import K_BAJ, K_SUB, THETA_MAX, V_MAX


def velocidad(theta):
    """Velocidad del rover segun la pendiente (lineal por tramos).

    Ecuacion de la velocidad en la memoria:
        subida (theta >= 0): baja hasta 0.2 * V_MAX en THETA_MAX
        bajada (theta < 0):  baja hasta 0.6 * V_MAX en -THETA_MAX
    Nunca supera V_MAX (Lema 1), que es lo que hace admisibles h1 y h2.

    Args:
        theta: Pendiente del paso (positiva = subida, negativa = bajada),
            en las mismas unidades que THETA_MAX.

    Returns:
        Velocidad en las mismas unidades que V_MAX.
    """
    if theta >= 0:
        return V_MAX * (1 - K_SUB * theta / THETA_MAX)
    return V_MAX * (1 - K_BAJ * -theta / THETA_MAX)


class RoverProblem:
    def __init__(self, terreno, inicio=None, objetivo=None):
        """Crea el problema de busqueda sobre un terreno.

        Args:
            terreno: Terreno con alturas, celdas transitables, inicio y
                objetivo por defecto.
            inicio: Celda (i, j) de partida. Si es None se usa
                terreno.inicio.
            objetivo: Celda (i, j) de llegada. Si es None se usa
                terreno.objetivo.
        """
        self.terreno = terreno
        self.initial = inicio if inicio is not None else terreno.inicio
        self.goal = objetivo if objetivo is not None else terreno.objetivo

    def actions(self, estado):
        """Devuelve los movimientos que el rover puede hacer desde estado.

        Args:
            estado: Celda actual (i, j).

        Returns:
            Lista de desplazamientos (di, dj) factibles; el terreno decide
            cuales lo son (dentro del mapa, celda transitable, pendiente
            no superior a THETA_MAX...).
        """
        return self.terreno.movimientos_factibles(estado)

    def result(self, estado, accion):
        """Modelo de transicion: aplica un desplazamiento a una celda.

        La accion no es "ir a la celda X" sino un desplazamiento relativo
        (di, dj), p.ej. (0, 1) = un paso a la derecha, (-1, -1) = diagonal
        arriba-izquierda. El nuevo estado es simplemente la suma
        componente a componente.

        Args:
            estado: Celda actual (i, j).
            accion: Desplazamiento (di, dj), tipicamente con di, dj en
                {-1, 0, 1}.

        Returns:
            Celda destino (i + di, j + dj).

        Example:
            >>> problema.result((3, 5), (1, -1))
            (4, 4)
        """
        return (estado[0] + accion[0], estado[1] + accion[1])

    def is_goal(self, estado):
        """Test objetivo.

        Args:
            estado: Celda (i, j) a comprobar.

        Returns:
            True si estado es la celda objetivo, False en otro caso.
        """
        return estado == self.goal

    def action_cost(self, estado, accion, siguiente):
        """Tiempo [s] del paso estado -> siguiente.

        Es la distancia recorrida (con la cuesta incluida) entre la
        velocidad a esa pendiente. Por eso es asimetrico: subir cuesta
        mas que bajar.

        Args:
            estado: Celda de origen (i, j).
            accion: Desplazamiento (di, dj) aplicado.
            siguiente: Celda destino, igual a result(estado, accion).

        Returns:
            Coste del paso en segundos.

        Example:
            Con S_CELL = 1 m, V_MAX = 0.042 m/s y THETA_MAX = 25 grados,
            paso a la derecha (0, 1) de una celda a 10.0 m a otra a 10.3 m:

                d_h      = 1 m                  (ortogonal; en diagonal 1.41 m)
                desnivel = 10.3 - 10.0 = 0.3 m  (> 0: sube)
                theta    = atan(0.3 / 1) = 16.7 grados
                v        = 0.042 * (1 - 0.8 * 16.7 / 25) = 0.0196 m/s
                d        = hypot(1, 0.3) = 1.044 m   (la rampa, no el suelo)
                coste    = 1.044 / 0.0196 = 53.4 s

            El mismo paso al reves (bajando) da theta = -16.7 grados,
            v = 0.042 * (1 - 0.4 * 16.7 / 25) = 0.0308 m/s y
            coste = 33.9 s. En llano serian 1 / 0.042 = 23.8 s.
        """
        d_h = self.terreno.distancia_horizontal(*accion)
        desnivel = self.terreno.alturas[siguiente] - self.terreno.alturas[estado]
        theta = self.terreno.pendiente(estado, siguiente)
        return math.hypot(d_h, desnivel) / velocidad(theta)
