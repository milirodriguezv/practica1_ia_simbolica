"""Tests del DPLLSolver con formulas pequenas que se pueden comprobar a mano.

Cada clausula es un conjunto de enteros (3 = x3, -3 = no x3).
"""

import pytest

from dpll_solver import DPLLSolver, LimiteSuperado


def satisface(clausulas, asignacion):
    """Cada clausula tiene al menos un literal verdadero."""
    for clausula in clausulas:
        if not any(asignacion.get(abs(l)) == (l > 0) for l in clausula):
            return False
    return True


def test_sin_clausulas_es_sat():
    assert DPLLSolver().solve([]) == {}


def test_contradiccion_es_unsat():
    assert DPLLSolver().solve([{1}, {-1}]) is None


def test_cadena_de_implicaciones():
    """x1, x1 -> x2, x2 -> x3: la unica solucion es todo verdadero y sale
    solo con clausulas unitarias, sin decidir nada."""
    solver = DPLLSolver()
    assert solver.solve([{1}, {-1, 2}, {-2, 3}]) == {1: True, 2: True, 3: True}
    assert solver.estadisticas.propagaciones == 3
    assert solver.estadisticas.decisiones == 0


def test_la_solucion_cumple_todas_las_clausulas():
    clausulas = [{1, 2, -3}, {-1, 3}, {-2, 3}, {3, 4}, {-4, -1}]
    solucion = DPLLSolver().solve(clausulas)
    assert solucion is not None
    assert satisface(clausulas, solucion)


def test_formula_unsat_con_dos_variables():
    """Las cuatro combinaciones de x1 y x2 estan prohibidas."""
    clausulas = [{1, 2}, {1, -2}, {-1, 2}, {-1, -2}]
    assert DPLLSolver().solve(clausulas) is None


def test_sin_las_reglas_la_respuesta_es_la_misma():
    """Quitar la clausula unitaria y el simbolo puro cambia cuanto se
    explora, pero no el resultado."""
    clausulas = [{1, 2, -3}, {-1, 3}, {-2, 3}, {3, 4}, {-4, -1}]
    solucion = DPLLSolver(usar_unitaria=False, usar_puro=False).solve(clausulas)
    assert satisface(clausulas, solucion)


def test_tope_de_llamadas():
    clausulas = [{1, 2}, {1, -2}, {-1, 2}, {-1, -2}]
    with pytest.raises(LimiteSuperado):
        DPLLSolver(max_llamadas=1).solve(clausulas)
