"""Tests del generador de terreno y de las reglas de movimiento."""

import math

import numpy as np
from parametros import THETA_MAX
from terrain import ParametrosGenerador, Terreno, generar_terreno

PARAMS_PEQUENOS = ParametrosGenerador(N=60, n_crateres=5)


def test_misma_semilla_mismo_mapa():
    a = generar_terreno(PARAMS_PEQUENOS, semilla=7)
    b = generar_terreno(PARAMS_PEQUENOS, semilla=7)
    assert np.array_equal(a.alturas, b.alturas)
    assert np.array_equal(a.rocas, b.rocas)
    assert (a.inicio, a.objetivo) == (b.inicio, b.objetivo)


def test_inicio_y_objetivo_validos():
    terreno = generar_terreno(PARAMS_PEQUENOS, semilla=3)
    assert terreno.es_transitable(terreno.inicio)
    assert terreno.es_transitable(terreno.objetivo)
    assert terreno.alcanzables_desde(terreno.inicio)[terreno.objetivo]


def test_no_se_cruza_entre_dos_rocas_por_la_esquina():
    alturas = np.zeros((3, 3))
    rocas = np.zeros((3, 3), dtype=bool)
    rocas[0, 1] = rocas[1, 0] = True
    terreno = Terreno(alturas, rocas)
    assert not terreno.es_movimiento_factible((1, 1), -1, -1)
    assert terreno.es_movimiento_factible((1, 1), 1, 1)


def test_pendiente_limite():
    """Un desnivel de tan(25) m en 1 m es justo el limite; algo mas ya no."""
    limite = math.tan(THETA_MAX)
    alturas = np.array([[0.0, limite - 1e-9, 2 * limite + 1e-6]])
    terreno = Terreno(alturas, np.zeros_like(alturas, dtype=bool))
    assert terreno.es_movimiento_factible((0, 0), 0, 1)
    assert not terreno.es_movimiento_factible((0, 1), 0, 1)
