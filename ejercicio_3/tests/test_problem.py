"""Tests del modelo de coste y de las heuristicas (paso 2).
Los valores esperados salen del ejemplo 4x4 de la memoria (Bloque D)."""

import math

import numpy as np
import pytest

from heuristics import h0, h1, h2
from parametros import S_CELL, THETA_MAX, V_MAX
from problem import RoverProblem, velocidad
from terrain import ParametrosGenerador, generar_terreno


def coste(problema, a, b):
    return problema.action_cost(a, (b[0] - a[0], b[1] - a[1]), b)


# ----------------------------- velocidad -----------------------------

def test_velocidad_acotada():
    """Lema 1: 0.2 * V_MAX <= v <= V_MAX, maximo solo en llano."""
    assert velocidad(0) == V_MAX
    for theta in np.linspace(-THETA_MAX, THETA_MAX, 201):
        assert 0.2 * V_MAX - 1e-12 <= velocidad(theta) <= V_MAX
    assert velocidad(THETA_MAX) == pytest.approx(0.2 * V_MAX)
    assert velocidad(-THETA_MAX) == pytest.approx(0.6 * V_MAX)


def test_subir_es_mas_lento_que_bajar():
    for theta in np.linspace(0.01, THETA_MAX, 20):
        assert velocidad(theta) < velocidad(-theta)


# ------------------------------- coste -------------------------------

def test_costes_del_ejemplo_4x4(mapa_4x4):
    p = RoverProblem(mapa_4x4)
    assert coste(p, (0, 0), (1, 0)) == pytest.approx(38.05, abs=0.01)
    assert coste(p, (1, 0), (2, 1)) == pytest.approx(55.81, abs=0.01)   # diagonal, subida
    assert coste(p, (2, 1), (3, 2)) == pytest.approx(39.03, abs=0.01)   # diagonal, bajada
    assert coste(p, (1, 3), (0, 3)) == pytest.approx(S_CELL / V_MAX)    # llano


def test_coste_asimetrico(mapa_4x4):
    p = RoverProblem(mapa_4x4)
    assert coste(p, (0, 0), (1, 0)) == pytest.approx(38.05, abs=0.01)   # sube 0.2 m
    assert coste(p, (1, 0), (0, 0)) == pytest.approx(29.65, abs=0.01)   # baja 0.2 m


def test_coste_minimo_positivo():
    """Lema 2: todo paso cuesta al menos s / V_MAX (~23.8 s)."""
    t = generar_terreno(ParametrosGenerador(N=40, n_crateres=4), semilla=5)
    p = RoverProblem(t)
    for i in range(t.N):
        for j in range(t.N):
            for di, dj in p.actions((i, j)):
                assert p.action_cost((i, j), (di, dj), (i + di, j + dj)) >= S_CELL / V_MAX - 1e-9


# ---------------------------- heuristicas ----------------------------

def test_valores_del_ejemplo_4x4(mapa_4x4):
    p = RoverProblem(mapa_4x4)
    assert h0((0, 0), p) == 0
    assert h1((0, 0), p) == pytest.approx(101.02, abs=0.01)
    assert h1((0, 1), p) == pytest.approx(85.85, abs=0.01)
    assert h2((0, 1), p) == pytest.approx(91.15, abs=0.01)
    assert h1((3, 3), p) == h2((3, 3), p) == 0


def test_admisibles_en_el_ejemplo_4x4(mapa_4x4):
    """h1 <= h2 <= h* con los h* de la tabla de la memoria."""
    h_estrella = {(0, 0): 166.82, (0, 1): 138.35, (0, 2): 109.07, (0, 3): 79.79,
                  (1, 0): 128.77, (1, 3): 55.98, (2, 0): 102.23, (2, 1): 72.96,
                  (2, 2): 51.88, (2, 3): 29.65, (3, 0): 97.12, (3, 1): 67.84,
                  (3, 2): 33.92, (3, 3): 0.0}
    p = RoverProblem(mapa_4x4)
    for n, real in h_estrella.items():
        assert h1(n, p) <= h2(n, p) <= real + 1e-9


def test_dominancia_e_igualdad():
    """Proposicion 3: h2 >= h1, iguales solo en la misma fila/columna/diagonal."""
    t = generar_terreno(ParametrosGenerador(N=30, n_crateres=2), semilla=1)
    p = RoverProblem(t, objetivo=(15, 15))
    for i in range(t.N):
        for j in range(t.N):
            di, dj = abs(i - 15), abs(j - 15)
            alineada = di == 0 or dj == 0 or di == dj
            assert h2((i, j), p) >= h1((i, j), p)
            assert (h2((i, j), p) == pytest.approx(h1((i, j), p))) == alineada


def test_consistencia_en_todas_las_aristas():
    """Proposicion 2: h(a) <= c(a, b) + h(b) en todo paso factible."""
    t = generar_terreno(ParametrosGenerador(N=40, n_crateres=4), semilla=2)
    p = RoverProblem(t)
    for i in range(t.N):
        for j in range(t.N):
            for di, dj in p.actions((i, j)):
                b = (i + di, j + dj)
                c = p.action_cost((i, j), (di, dj), b)
                for h in (h1, h2):
                    assert h((i, j), p) <= c + h(b, p) + 1e-9

