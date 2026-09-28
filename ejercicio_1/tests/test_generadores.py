"""Tests de los generadores de instancias aleatorias."""

from environment import Environment
from generadores import cnf_aleatoria, grafo_aleatorio
from logical_agent import LogicalAgent


def test_cnf_reproducible_y_bien_formada():
    f = cnf_aleatoria(20, 85, semilla=7)
    assert f == cnf_aleatoria(20, 85, semilla=7)
    assert f != cnf_aleatoria(20, 85, semilla=8)
    assert len(f) == 85
    for clausula in f:
        assert len({abs(l) for l in clausula}) == 3  # 3 variables distintas
        assert all(1 <= abs(l) <= 20 for l in clausula)


def test_grafo_reproducible_y_bien_formado():
    g = grafo_aleatorio(30, grado_medio=4, semilla=3)
    assert g == grafo_aleatorio(30, grado_medio=4, semilla=3)
    assert len(g["regiones"]) == 30
    assert len(g["adyacencias"]) == 60  # 30 * 4 / 2
    assert len({frozenset(a) for a in g["adyacencias"]}) == 60  # sin repetidas
    assert all(a != b for a, b in g["adyacencias"])  # sin bucles


def test_grafo_aleatorio_se_colorea():
    g = grafo_aleatorio(30, grado_medio=3, semilla=0)
    entorno = Environment(g["regiones"], g["adyacencias"], ["A", "B", "C", "D"])
    asignacion = LogicalAgent().run(entorno)
    assert asignacion is not None and entorno.goal_test(asignacion)
