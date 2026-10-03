"""Constantes fisicas del rover.

Corresponden a la tabla "Parametros fisicos del modelo" de la
memoria. Estan en un unico sitio porque las usan varios modulos:

    - terrain.py    -> THETA_MAX y S_CELL, para decidir que movimientos
                       son factibles (pendiente, rocas)
    - problem.py    -> todas, para el modelo de coste c(a,b) = d / v(theta)
    - heuristics.py -> V_MAX y S_CELL, para h1 y h2

Si se cambia un valor aqui, cambia en todo el ejercicio a la vez.
"""

import math

# Lado de cada celda [m]. Resolucion de los modelos de terreno HiRISE.
S_CELL = 1.0

# Velocidad maxima en llano [m/s] (~150 m/h, Perseverance / Curiosity).
V_MAX = 0.042

# Pendiente maxima permitida en un movimiento [rad]. Margen bajo los 30 grados
# que el software de Curiosity no deja superar.
THETA_MAX = math.radians(25)

# Perdida relativa de velocidad al llegar a THETA_MAX:
#   subida -> v = (1 - 0.8) * V_MAX = 0.2 * V_MAX  (patina)
#   bajada -> v = (1 - 0.4) * V_MAX = 0.6 * V_MAX  (frena por seguridad)
K_SUB = 0.8
K_BAJ = 0.4

# Las 8 direcciones de movimiento (di, dj): 4 ortogonales + 4 diagonales.
DIRECCIONES = [(-1, -1), (-1, 0), (-1, 1),
               (0, -1),           (0, 1),
               (1, -1),  (1, 0),  (1, 1)]
