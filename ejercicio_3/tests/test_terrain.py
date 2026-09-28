"""Tests del generador de terreno y de las reglas de movimiento (paso 1)."""

import math

import numpy as np
import pytest
from parametros import DIRECCIONES, THETA_MAX
from terrain import (
    ParametrosGenerador,
    Terreno,
    altura_crater,
    cargar_terreno,
    generar_terreno,
    guardar_terreno,
)

PARAMS_PEQUENOS = ParametrosGenerador(N=60, n_crateres=5)


@pytest.fixture(scope="module")
def terreno():
    return generar_terreno(PARAMS_PEQUENOS, semilla=3)


def test_misma_semilla_mismo_mapa():
    a = generar_terreno(PARAMS_PEQUENOS, semilla=7)
    b = generar_terreno(PARAMS_PEQUENOS, semilla=7)
    assert np.array_equal(a.alturas, b.alturas)
    assert np.array_equal(a.rocas, b.rocas)
    assert (a.inicio, a.objetivo) == (b.inicio, b.objetivo)


def test_inicio_y_objetivo_validos(terreno):
    assert terreno.es_transitable(terreno.inicio)
    assert terreno.es_transitable(terreno.objetivo)
    distancia = terreno.s * math.dist(terreno.inicio, terreno.objetivo)
    assert distancia >= PARAMS_PEQUENOS.separacion_min * terreno.N * terreno.s
    assert terreno.alcanzables_desde(terreno.inicio)[terreno.objetivo]


def test_factibilidad_coincide_con_las_reglas(terreno):
    """La tabla precalculada debe dar lo mismo que aplicar las reglas i-iv a mano."""
    rng = np.random.default_rng(0)
    for _ in range(2000):
        a = tuple(int(x) for x in rng.integers(0, terreno.N, size=2))
        di, dj = DIRECCIONES[rng.integers(len(DIRECCIONES))]
        b = (a[0] + di, a[1] + dj)
        esperado = (
            terreno.es_transitable(a)
            and terreno.es_transitable(b)
            and abs(terreno.pendiente(a, b)) <= THETA_MAX
            and not (
                di
                and dj
                and (terreno.rocas[a[0] + di, a[1]] or terreno.rocas[a[0], a[1] + dj])
            )
        )
        assert terreno.es_movimiento_factible(a, di, dj) == esperado


def test_factibilidad_simetrica(terreno):
    for i in range(terreno.N):
        for j in range(terreno.N):
            for vecina in terreno.vecinos_factibles((i, j)):
                assert (i, j) in terreno.vecinos_factibles(vecina)


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


def test_pared_del_crater_es_arctan_4_rho():
    """En el cuenco parabolico, la pendiente junto al borde es arctan(4 rho)."""
    radio, rho = 10.0, 0.15
    profundidad = rho * 2 * radio
    r = np.array([radio - 1e-4, radio])
    h = altura_crater(r, radio, profundidad, eta=0.0, w=0.3)
    pendiente = math.atan((h[1] - h[0]) / 1e-4)
    assert pendiente == pytest.approx(math.atan(4 * rho), rel=1e-3)


def test_guardar_y_cargar(terreno, tmp_path):
    ruta = tmp_path / "mapa.npz"
    guardar_terreno(terreno, ruta, PARAMS_PEQUENOS)
    cargado = cargar_terreno(ruta)
    assert np.array_equal(cargado.alturas, terreno.alturas)
    assert np.array_equal(cargado.rocas, terreno.rocas)
    assert (cargado.inicio, cargado.objetivo, cargado.semilla) == (
        terreno.inicio,
        terreno.objetivo,
        terreno.semilla,
    )
