"""Tests de la busqueda y de b* (paso 3).
El coste optimo del 4x4 (166.82 s) es la suma de los pasos de la ruta de
la memoria: 38.05 + 55.81 + 39.03 + 33.93. En mapas generados, el coste
de referencia lo da networkx (Dijkstra), que es independiente de search.py."""

import math

import networkx as nx
import pytest

from heuristics import h1, h2
from metrics import b_estrella, factor_ramificacion_efectivo
from problem import RoverProblem
from search import astar_search, greedy_search, uniform_cost_search
from terrain import ParametrosGenerador, Terreno, generar_terreno

RUTA_OPTIMA_4X4 = [(0, 0), (1, 0), (2, 1), (3, 2), (3, 3)]
COSTE_OPTIMO_4X4 = 166.82
PARAMS_PEQUENOS = ParametrosGenerador(N=40, n_crateres=4)
SEMILLAS = range(5)


def todos(problema):
    """Los algoritmos que deben dar el optimo (h admisible y consistente)."""
    return {
        "UCS": uniform_cost_search(problema),
        "A* h1": astar_search(problema, h1),
        "A* h2": astar_search(problema, h2),
    }


def coste_networkx(problema):
    """Coste optimo de S a G con Dijkstra de networkx sobre el mismo grafo."""
    grafo = nx.DiGraph()
    t = problema.terreno
    for i in range(t.N):
        for j in range(t.N):
            for accion in problema.actions((i, j)):
                hijo = problema.result((i, j), accion)
                grafo.add_edge((i, j), hijo, weight=problema.action_cost((i, j), accion, hijo))
    return nx.dijkstra_path_length(grafo, problema.initial, problema.goal)


def comprobar_ruta(problema, resultado):
    """La ruta empieza en S, acaba en G, cada paso es factible y la suma
    de los costes de los pasos es el coste devuelto."""
    ruta = resultado.ruta
    assert ruta[0] == problema.initial and ruta[-1] == problema.goal
    total = 0.0
    for a, b in zip(ruta, ruta[1:]):
        accion = (b[0] - a[0], b[1] - a[1])
        assert accion in problema.actions(a)
        total += problema.action_cost(a, accion, b)
    assert total == pytest.approx(resultado.coste)


# ------------------------- ejemplo 4x4 a mano -------------------------

def test_ruta_optima_4x4(mapa_4x4):
    p = RoverProblem(mapa_4x4)
    for nombre, r in todos(p).items():
        assert r.ruta == RUTA_OPTIMA_4X4, nombre
        assert r.coste == pytest.approx(COSTE_OPTIMO_4X4, abs=0.01), nombre
        comprobar_ruta(p, r)


def test_voraz_no_es_optima_4x4(mapa_4x4):
    """La voraz va por arriba, que parece mas directo pero tarda mas."""
    r = greedy_search(RoverProblem(mapa_4x4), h2)
    assert r.coste == pytest.approx(167.63, abs=0.01)
    assert r.coste > COSTE_OPTIMO_4X4
    assert r.ruta == [(0, 0), (0, 1), (0, 2), (0, 3), (1, 3), (2, 3), (3, 3)]


def test_contadores_4x4(mapa_4x4):
    """Valores de la traza vuelta a vuelta de A* + h2 (notas, seccion 6)."""
    r = astar_search(RoverProblem(mapa_4x4), h2)
    assert (r.expandidos, r.generados, r.frontera_max) == (12, 18, 8)
    assert r.orden_expansion[:3] == [(0, 0), (0, 1), (1, 0)]
    assert r.orden_expansion[-1] == (3, 3)
    assert r.profundidad == 4


def test_sin_camino(mapa_4x4):
    """G rodeada de rocas: se expande todo lo alcanzable y no hay ruta."""
    rocas = mapa_4x4.rocas.copy()
    rocas[2, 2] = rocas[2, 3] = rocas[3, 2] = True
    t = Terreno(mapa_4x4.alturas, rocas, inicio=(0, 0), objetivo=(3, 3))
    for nombre, r in todos(RoverProblem(t)).items():
        assert r.ruta is None and r.coste == math.inf, nombre
        assert r.expandidos == t.alcanzables_desde((0, 0)).sum(), nombre


def test_inicio_es_objetivo(mapa_4x4):
    r = astar_search(RoverProblem(mapa_4x4, inicio=(0, 0), objetivo=(0, 0)), h2)
    assert r.ruta == [(0, 0)] and r.coste == 0 and r.expandidos == 1
    assert r.profundidad == 0


# ----------------------- mapas generados (N = 40) ----------------------

@pytest.mark.parametrize("semilla", SEMILLAS)
def test_coste_igual_a_networkx(semilla):
    """E1 en pequeno: UCS = A*(h1) = A*(h2) = Dijkstra de networkx."""
    p = RoverProblem(generar_terreno(PARAMS_PEQUENOS, semilla=semilla))
    optimo = coste_networkx(p)
    for nombre, r in todos(p).items():
        assert r.coste == pytest.approx(optimo), nombre
        comprobar_ruta(p, r)


@pytest.mark.parametrize("semilla", SEMILLAS)
def test_mejor_heuristica_expande_menos(semilla):
    """h2 >= h1 >= 0 (dominancia) -> A*(h2) no expande mas que A*(h1),
    y este no mas que UCS."""
    r = todos(RoverProblem(generar_terreno(PARAMS_PEQUENOS, semilla=semilla)))
    assert r["A* h2"].expandidos <= r["A* h1"].expandidos <= r["UCS"].expandidos


@pytest.mark.parametrize("semilla", SEMILLAS)
def test_voraz_nunca_mejora_el_optimo(semilla):
    p = RoverProblem(generar_terreno(PARAMS_PEQUENOS, semilla=semilla))
    r = greedy_search(p, h2)
    assert r.coste >= uniform_cost_search(p).coste - 1e-9
    comprobar_ruta(p, r)


def test_consistente_no_reexpande():
    """Con h consistente la primera expansion de cada celda ya tiene su
    mejor g, asi que ninguna celda se expande dos veces."""
    p = RoverProblem(generar_terreno(PARAMS_PEQUENOS, semilla=0))
    for nombre, r in todos(p).items():
        assert len(r.orden_expansion) == len(set(r.orden_expansion)), nombre
        assert r.expandidos == len(r.orden_expansion), nombre


# -------------------------------- b* --------------------------------

def test_b_estrella_ejemplo_del_libro():
    """AIMA 3.6.1: N = 52, d = 5 -> b* = 1.92."""
    assert factor_ramificacion_efectivo(52, 5) == pytest.approx(1.92, abs=0.005)


def test_b_estrella_arboles_exactos():
    assert factor_ramificacion_efectivo(5, 5) == pytest.approx(1.0, abs=1e-5)  # una sola rama
    assert factor_ramificacion_efectivo(3 + 9, 2) == pytest.approx(3.0, abs=1e-5)
    assert factor_ramificacion_efectivo(2 + 4 + 8, 3) == pytest.approx(2.0, abs=1e-5)


def test_b_estrella_profundidad_grande():
    """Rutas reales (d ~ 100, N ~ 10^4): no debe desbordar y debe cumplir
    la ecuacion."""
    b = factor_ramificacion_efectivo(10_000, 150)
    assert 1 < b < 1.1
    assert sum(b**i for i in range(1, 151)) == pytest.approx(10_000, rel=1e-3)


def test_b_estrella_casos_limite():
    assert factor_ramificacion_efectivo(0, 0) is None  # S = G
    with pytest.raises(ValueError):
        factor_ramificacion_efectivo(2, 5)             # imposible: N < d


def test_b_estrella_de_un_resultado(mapa_4x4):
    """A* + h2 en el 4x4: 18 generados (17 sin S) y d = 4."""
    r = astar_search(RoverProblem(mapa_4x4), h2)
    b = b_estrella(r)
    assert sum(b**i for i in range(1, 5)) == pytest.approx(17, abs=1e-4)
    assert b_estrella(uniform_cost_search(RoverProblem(mapa_4x4))) >= 1


def test_b_estrella_ordena_las_heuristicas():
    """Mejor heuristica -> menos nodos a igual d -> b* mas cerca de 1."""
    p = RoverProblem(generar_terreno(PARAMS_PEQUENOS, semilla=1))
    r = todos(p)
    assert b_estrella(r["A* h2"]) <= b_estrella(r["A* h1"]) + 1e-9
    assert b_estrella(r["A* h1"]) <= b_estrella(r["UCS"]) + 1e-9
