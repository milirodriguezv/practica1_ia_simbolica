"""Tests del modelo de coste y de las heuristicas.
Los valores esperados salen del ejemplo 4x4 hecho a mano."""

import pytest

from heuristics import h0, h1, h2
from parametros import S_CELL, THETA_MAX, V_MAX
from problem import RoverProblem, velocidad


def coste(problema, a, b):
    return problema.action_cost(a, (b[0] - a[0], b[1] - a[1]), b)


def test_velocidad_en_los_extremos():
    assert velocidad(0) == V_MAX
    assert velocidad(THETA_MAX) == pytest.approx(0.2 * V_MAX)    # subida maxima
    assert velocidad(-THETA_MAX) == pytest.approx(0.6 * V_MAX)   # bajada maxima


def test_costes_del_ejemplo_4x4(mapa_4x4):
    p = RoverProblem(mapa_4x4)
    assert coste(p, (0, 0), (1, 0)) == pytest.approx(38.05, abs=0.01)
    assert coste(p, (1, 0), (2, 1)) == pytest.approx(55.81, abs=0.01)   # diagonal, subida
    assert coste(p, (2, 1), (3, 2)) == pytest.approx(39.03, abs=0.01)   # diagonal, bajada
    assert coste(p, (1, 3), (0, 3)) == pytest.approx(S_CELL / V_MAX)    # llano


def test_subir_cuesta_mas_que_bajar(mapa_4x4):
    p = RoverProblem(mapa_4x4)
    assert coste(p, (0, 0), (1, 0)) == pytest.approx(38.05, abs=0.01)   # sube 0.2 m
    assert coste(p, (1, 0), (0, 0)) == pytest.approx(29.65, abs=0.01)   # baja 0.2 m


def test_heuristicas_del_ejemplo_4x4(mapa_4x4):
    p = RoverProblem(mapa_4x4)
    assert h0((0, 0), p) == 0
    assert h1((0, 0), p) == pytest.approx(101.02, abs=0.01)
    assert h1((0, 1), p) == pytest.approx(85.85, abs=0.01)
    assert h2((0, 1), p) == pytest.approx(91.15, abs=0.01)
    assert h1((3, 3), p) == h2((3, 3), p) == 0


def test_heuristicas_admisibles_en_el_ejemplo_4x4(mapa_4x4):
    """h1 <= h2 <= coste real hasta G (calculado a mano para cada celda)."""
    coste_real = {(0, 0): 166.82, (0, 1): 138.35, (0, 2): 109.07, (0, 3): 79.79,
                  (1, 0): 128.77, (1, 3): 55.98, (2, 0): 102.23, (2, 1): 72.96,
                  (2, 2): 51.88, (2, 3): 29.65, (3, 0): 97.12, (3, 1): 67.84,
                  (3, 2): 33.92, (3, 3): 0.0}
    p = RoverProblem(mapa_4x4)
    for celda, real in coste_real.items():
        assert h1(celda, p) <= h2(celda, p) <= real + 1e-9
