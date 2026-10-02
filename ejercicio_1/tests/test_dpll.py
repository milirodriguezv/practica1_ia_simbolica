"""Tests del DPLLSolver.

Clausulas en el formato del solver: cada clausula es un conjunto de
enteros (literal positivo = variable, negativo = variable negada).

La referencia independiente es la fuerza bruta: probar las 2^n
asignaciones. Solo vale para n pequeno, pero no comparte nada de codigo
con DPLL.
"""

import itertools
import random

import pytest

from dpll_solver import DPLLSolver
from generadores import cnf_aleatoria


def satisface(clausulas, asignacion):
    """Cada clausula tiene al menos un literal verdadero. Una variable sin
    asignar no hace verdadero a ningun literal (DPLL puede dejar variables
    libres si ya no influyen)."""
    for clausula in clausulas:
        if not any(asignacion.get(abs(l)) == (l > 0) for l in clausula):
            return False
    return True


def satisfacible_fuerza_bruta(clausulas):
    variables = sorted({abs(l) for c in clausulas for l in c})
    for valores in itertools.product([False, True], repeat=len(variables)):
        if satisface(clausulas, dict(zip(variables, valores))):
            return True
    return False


def palomar(n_palomas, n_huecos):
    """Principio del palomar: n_palomas en n_huecos, cada hueco con como
    mucho una paloma. UNSAT si n_palomas > n_huecos. Variable de la paloma
    p en el hueco h: p * n_huecos + h + 1."""
    var = lambda p, h: p * n_huecos + h + 1
    clausulas = [{var(p, h) for h in range(n_huecos)} for p in range(n_palomas)]
    for h in range(n_huecos):
        for p1, p2 in itertools.combinations(range(n_palomas), 2):
            clausulas.append({-var(p1, h), -var(p2, h)})
    return clausulas


# --------------------------- casos conocidos ---------------------------

def test_sin_clausulas_es_sat():
    assert DPLLSolver().solve([]) == {}


def test_clausula_vacia_es_unsat():
    assert DPLLSolver().solve([{1, 2}, set()]) is None


def test_contradiccion_directa_es_unsat():
    assert DPLLSolver().solve([{1}, {-1}]) is None


def test_cadena_de_implicaciones():
    """x1, x1 -> x2, x2 -> x3: la unica solucion es todo verdadero."""
    clausulas = [{1}, {-1, 2}, {-2, 3}]
    assert DPLLSolver().solve(clausulas) == {1: True, 2: True, 3: True}


def test_solucion_satisface_todas_las_clausulas():
    clausulas = [{1, 2, -3}, {-1, 3}, {-2, 3}, {3, 4}, {-4, -1}]
    solucion = DPLLSolver().solve(clausulas)
    assert solucion is not None
    assert satisface(clausulas, solucion)


@pytest.mark.parametrize("palomas, huecos, sat", [(2, 2, True), (3, 3, True),
                                                  (3, 2, False), (4, 3, False)])
def test_palomar(palomas, huecos, sat):
    solucion = DPLLSolver().solve(palomar(palomas, huecos))
    assert (solucion is not None) == sat


# ------------------- comparacion con fuerza bruta -------------------

@pytest.mark.parametrize("semilla", range(40))
def test_igual_que_fuerza_bruta(semilla):
    """3-CNF aleatorias de 8 variables. La razon clausulas/variables se
    reparte entre 2 y 7 para que salgan casos SAT y UNSAT."""
    n = 8
    clausulas = cnf_aleatoria(n, random.Random(semilla).randint(2 * n, 7 * n), semilla)
    solucion = DPLLSolver().solve(clausulas)
    assert (solucion is not None) == satisfacible_fuerza_bruta(clausulas)
    if solucion is not None:
        assert satisface(clausulas, solucion)


def test_fuerza_bruta_da_casos_sat_y_unsat():
    """Que el test anterior de verdad pruebe los dos resultados."""
    resultados = set()
    for semilla in range(40):
        clausulas = cnf_aleatoria(8, random.Random(semilla).randint(16, 56), semilla)
        resultados.add(satisfacible_fuerza_bruta(clausulas))
    assert resultados == {True, False}


# ------------------- ablacion y estadisticas (paso 2) -------------------

CONFIGURACIONES = [(True, True), (True, False), (False, True), (False, False)]


@pytest.mark.parametrize("unitaria, puro", CONFIGURACIONES)
@pytest.mark.parametrize("semilla", range(15))
def test_ablacion_sigue_siendo_correcta(semilla, unitaria, puro):
    """Quitar las reglas 2 y 3 cambia cuanto se explora, no la respuesta."""
    clausulas = cnf_aleatoria(8, random.Random(semilla).randint(16, 56), semilla)
    solucion = DPLLSolver(usar_unitaria=unitaria, usar_puro=puro).solve(clausulas)
    assert (solucion is not None) == satisfacible_fuerza_bruta(clausulas)
    if solucion is not None:
        assert satisface(clausulas, solucion)


def test_estadisticas_cadena_de_implicaciones():
    """x1, x1 -> x2, x2 -> x3: todo sale por propagacion, sin decidir nada."""
    solver = DPLLSolver()
    solver.solve([{1}, {-1, 2}, {-2, 3}])
    e = solver.estadisticas
    assert (e.propagaciones, e.decisiones, e.retrocesos, e.conflictos) == (3, 0, 0, 0)
    assert e.llamadas == 4  # la inicial + una por propagacion
    assert e.tiempo > 0


def test_sin_unitaria_hay_que_decidir():
    solver = DPLLSolver(usar_unitaria=False, usar_puro=False)
    solver.solve([{1}, {-1, 2}, {-2, 3}])
    assert solver.estadisticas.propagaciones == 0
    assert solver.estadisticas.decisiones > 0


def test_unsat_cuenta_conflictos_y_retrocesos():
    solver = DPLLSolver()
    assert solver.solve(palomar(3, 2)) is None
    e = solver.estadisticas
    assert e.conflictos > 0 and e.retrocesos > 0
    assert e.retrocesos <= e.decisiones  # solo se retrocede de un valor probado


def test_estadisticas_se_reinician_en_cada_solve():
    solver = DPLLSolver()
    solver.solve(palomar(4, 3))
    solver.solve([{1}])
    assert solver.estadisticas.propagaciones == 1
    assert solver.estadisticas.decisiones == 0


def test_propagacion_reduce_la_busqueda():
    """Sobre el palomar UNSAT, las reglas 2 y 3 reducen las llamadas."""
    completo, basico = DPLLSolver(), DPLLSolver(usar_unitaria=False, usar_puro=False)
    completo.solve(palomar(4, 3))
    basico.solve(palomar(4, 3))
    assert completo.estadisticas.llamadas < basico.estadisticas.llamadas
