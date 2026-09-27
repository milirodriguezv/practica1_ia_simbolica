"""
run_experiments.py
------------------
Experimentos de la seccion de Resultados (guia, seccion 7). Cada uno
escribe un CSV en results/:

    E1  correccion: coste A*(h1) = A*(h2) = UCS = networkx
    E2  heuristicas: nodos generados y b* frente a la profundidad d
    E3  voraz frente a A*: sobrecoste (%) de la voraz
    E4  asimetria: coste de S -> G frente a G -> S
    E5  escalabilidad: N = 50, 100, 200, 400

Semillas fijas y 20-50 mapas por configuracion.

PASO 5 -- pendiente de implementar.
"""

from pathlib import Path

CARPETA_RESULTADOS = Path(__file__).parent / "results"


if __name__ == "__main__":
    raise NotImplementedError
