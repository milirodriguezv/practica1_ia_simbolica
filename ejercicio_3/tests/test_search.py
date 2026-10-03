"""Tests de la busqueda y de b*.
El coste optimo del 4x4 (166.82 s) es la suma de los pasos de la ruta
hecha a mano: 38.05 + 55.81 + 39.03 + 33.93. En un mapa generado, el
coste de referencia lo da networkx (Dijkstra)."""

import networkx as nx
import pytest

from heuristics import h1, h2
from metrics import factor_ramificacion_efectivo
from problem import RoverProblem
from search import astar_search, greedy_search, uniform_cost_search
from terrain import ParametrosGenerador, Terreno, generar_terreno

RUTA_OPTIMA_4X4 = [(0, 0), (1, 0), (2, 1), (3, 2), (3, 3)]
COSTE_OPTIMO_4X4 = 166.82


def test_ruta_optima_4x4(mapa_4x4):
    """UCS, A*(h1) y A*(h2) encuentran la misma ruta optima."""
    p = RoverProblem(mapa_4x4)
    for r in [uniform_cost_search(p), astar_search(p, h1), astar_search(p, h2)]:
        assert r.ruta == RUTA_OPTIMA_4X4
        assert r.coste == pytest.approx(COSTE_OPTIMO_4X4, abs=0.01)


def test_voraz_no_es_optima_4x4(mapa_4x4):
    """La voraz va por arriba, que parece mas directo pero tarda mas."""
    r = greedy_search(RoverProblem(mapa_4x4), h2)
    assert r.ruta == [(0, 0), (0, 1), (0, 2), (0, 3), (1, 3), (2, 3), (3, 3)]
    assert r.coste == pytest.approx(167.63, abs=0.01)
    assert r.coste > COSTE_OPTIMO_4X4


def test_sin_camino(mapa_4x4):
    """G rodeada de rocas: no hay ruta."""
    rocas = mapa_4x4.rocas.copy()
    rocas[2, 2] = rocas[2, 3] = rocas[3, 2] = True
    terreno = Terreno(mapa_4x4.alturas, rocas, inicio=(0, 0), objetivo=(3, 3))
    r = astar_search(RoverProblem(terreno), h2)
    assert r.ruta is None


def test_mismo_coste_que_networkx():
    """En un mapa generado de 40 x 40, A* da el mismo coste que el
    Dijkstra de networkx sobre el mismo grafo de movimientos."""
    terreno = generar_terreno(ParametrosGenerador(N=40, n_crateres=4), semilla=0)
    p = RoverProblem(terreno)

    grafo = nx.DiGraph()
    for i in range(terreno.N):
        for j in range(terreno.N):
            for accion in p.actions((i, j)):
                hijo = p.result((i, j), accion)
                grafo.add_edge((i, j), hijo, weight=p.action_cost((i, j), accion, hijo))
    referencia = nx.dijkstra_path_length(grafo, p.initial, p.goal)

    assert astar_search(p, h2).coste == pytest.approx(referencia)
    assert uniform_cost_search(p).coste == pytest.approx(referencia)


def test_mejor_heuristica_expande_menos():
    terreno = generar_terreno(ParametrosGenerador(N=40, n_crateres=4), semilla=0)
    p = RoverProblem(terreno)
    ucs = uniform_cost_search(p).expandidos
    con_h1 = astar_search(p, h1).expandidos
    con_h2 = astar_search(p, h2).expandidos
    assert con_h2 <= con_h1 <= ucs


def test_b_estrella_ejemplo_del_libro():
    """AIMA 3.6.1: N = 52, d = 5 -> b* = 1.92."""
    assert factor_ramificacion_efectivo(52, 5) == pytest.approx(1.92, abs=0.005)
