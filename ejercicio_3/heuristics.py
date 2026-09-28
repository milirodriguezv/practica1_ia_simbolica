"""
heuristics.py
-------------
Heuristicas obtenidas por RELAJACION del problema (memoria,
"Heuristicas"; libro 4a ed. seccion 3.6.2). Todas estiman el tiempo
que falta hasta G como "distancia / V_MAX", es decir, como si el
terreno fuese llano y sin obstaculos:

    h0(n) = 0                          -> A* se convierte en UCS
    h1(n) = d_euclidea(n, G) / V_MAX   -> ademas, en linea recta (sin cuadricula)
    h2(n) = d_octil(n, G)    / V_MAX   -> con 8-conectividad

h1 y h2 son admisibles y consistentes, y h2 >= h1 (memoria,
Proposiciones 1-3). Firma comun: h(estado, problema).
"""

import math

from parametros import V_MAX


def h0(estado, problema):
    return 0.0


def h1(estado, problema):
    """Distancia en linea recta hasta G, a velocidad maxima."""
    di = abs(estado[0] - problema.goal[0])
    dj = abs(estado[1] - problema.goal[1])
    return problema.terreno.s * math.hypot(di, dj) / V_MAX


def h2(estado, problema):
    """Distancia octil hasta G (min(di, dj) diagonales + el resto rectos),
    a velocidad maxima: s * (max + (sqrt(2) - 1) * min) / V_MAX."""
    di = abs(estado[0] - problema.goal[0])
    dj = abs(estado[1] - problema.goal[1])
    return problema.terreno.s * (max(di, dj) + (math.sqrt(2) - 1) * min(di, dj)) / V_MAX

