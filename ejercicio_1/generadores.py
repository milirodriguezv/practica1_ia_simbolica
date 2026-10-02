"""
generadores.py
--------------
Instancias aleatorias para los experimentos. Todo depende de una
semilla: la misma semilla da siempre la misma instancia.

    cnf_aleatoria    k-SAT aleatorio (libro 4a ed. seccion 7.6.3): m
                     clausulas de k literales sobre n variables. Con k = 3
                     la probabilidad de SAT cae de ~1 a ~0 alrededor de
                     m/n = 4.26 (transicion de fase), donde DPLL tarda mas.
    grafo_aleatorio  grafo aleatorio G(n, m) con grado medio dado, en el
                     mismo formato que mapas.py, para colorearlo.
"""

import random


def cnf_aleatoria(n_variables, n_clausulas, semilla, k=3):
    """Cada clausula: k variables distintas elegidas al azar, cada una
    negada con probabilidad 1/2. Formato del solver (conjuntos de enteros)."""
    rng = random.Random(semilla)
    clausulas = []
    for _ in range(n_clausulas):
        variables = rng.sample(range(1, n_variables + 1), k)
        clausulas.append({v if rng.random() < 0.5 else -v for v in variables})
    return clausulas


def grafo_aleatorio(n_regiones, grado_medio, semilla):
    """n regiones y n * grado_medio / 2 fronteras distintas elegidas al azar
    entre todos los pares posibles. Las posiciones (al azar en [0, 10]^2)
    solo sirven para dibujarlo."""
    rng = random.Random(semilla)
    regiones = [f"R{i}" for i in range(n_regiones)]
    n_fronteras = round(n_regiones * grado_medio / 2)
    pares = [(a, b) for i, a in enumerate(regiones) for b in regiones[i + 1:]]
    return {
        "regiones": regiones,
        "adyacencias": rng.sample(pares, n_fronteras),
        "posiciones": {r: (rng.uniform(0, 10), rng.uniform(0, 10)) for r in regiones},
    }
