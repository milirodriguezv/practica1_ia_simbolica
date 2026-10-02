"""Tests del coloreado de grafos: la traduccion a clausulas, el entorno y
el agente completo (TELL -> ASK -> goal_test)."""

import itertools
from math import comb

import networkx as nx
import pytest
from environment import Environment
from graph_coloring import crear_variables, generar_clausulas
from logical_agent import LogicalAgent
from mapas import AUSTRALIA, EEUU, VECINOS_EEUU

REGIONES, ADYACENCIAS = AUSTRALIA["regiones"], AUSTRALIA["adyacencias"]

TRES_COLORES = ["Rojo", "Verde", "Azul"]


def resolver(regiones, adyacencias, colores):
    entorno = Environment(regiones, adyacencias, colores)
    asignacion = LogicalAgent().run(entorno)
    return entorno, asignacion


def test_una_variable_por_region_y_color():
    variables = crear_variables(REGIONES, TRES_COLORES)
    assert len(variables) == len(REGIONES) * len(TRES_COLORES)
    assert sorted(variables.values()) == list(range(1, 22))


def test_numero_de_clausulas():
    """n (al menos un color) + n * C(k, 2) (a lo sumo uno) + |E| * k (vecinos)."""
    n, k, e = len(REGIONES), len(TRES_COLORES), len(ADYACENCIAS)
    variables = crear_variables(REGIONES, TRES_COLORES)
    clausulas = generar_clausulas(REGIONES, TRES_COLORES, ADYACENCIAS, variables)
    assert len(clausulas) == n + n * comb(k, 2) + e * k


def test_australia_con_3_colores():
    entorno, asignacion = resolver(REGIONES, ADYACENCIAS, TRES_COLORES)
    assert asignacion is not None
    coloreado = entorno.decodificar(asignacion)
    assert set(coloreado) == set(REGIONES)
    for a, b in ADYACENCIAS:
        assert coloreado[a] != coloreado[b]


def test_australia_con_2_colores_es_unsat():
    """WA, NT y SA forman un triangulo: hacen falta 3 colores."""
    _, asignacion = resolver(REGIONES, ADYACENCIAS, ["Rojo", "Verde"])
    assert asignacion is None


@pytest.mark.parametrize("n, colores, sat", [(3, 3, True), (4, 3, False), (4, 4, True)])
def test_grafo_completo(n, colores, sat):
    """K_n necesita exactamente n colores."""
    regiones = [f"R{i}" for i in range(n)]
    adyacencias = list(itertools.combinations(regiones, 2))
    _, asignacion = resolver(regiones, adyacencias, [f"C{i}" for i in range(colores)])
    assert (asignacion is not None) == sat


def test_goal_test_rechaza_vecinos_del_mismo_color():
    entorno = Environment(REGIONES, ADYACENCIAS, TRES_COLORES)
    todo_rojo = {entorno.variable_id[(r, "Rojo")]: True for r in REGIONES}
    assert not entorno.goal_test(todo_rojo)


def test_goal_test_rechaza_regiones_sin_color():
    entorno = Environment(REGIONES, ADYACENCIAS, TRES_COLORES)
    assert not entorno.goal_test({})


# ------------------------------ EE. UU. ------------------------------


def test_vecinos_eeuu_simetricos():
    for estado, vecinos in VECINOS_EEUU.items():
        for vecino in vecinos:
            assert estado in VECINOS_EEUU[vecino], (
                f"{estado}-{vecino} solo en un sentido"
            )


def test_grafo_eeuu():
    """48 estados contiguos y 105 fronteras; conexo y plano (es un mapa)."""
    grafo = nx.Graph(EEUU["adyacencias"])
    assert grafo.number_of_nodes() == 48 == len(EEUU["regiones"])
    assert grafo.number_of_edges() == 105
    assert nx.is_connected(grafo)
    assert nx.check_planarity(grafo)[0]
    assert set(EEUU["posiciones"]) == set(EEUU["regiones"])


@pytest.mark.parametrize("n_colores, sat", [(3, False), (4, True)])
def test_eeuu_necesita_4_colores(n_colores, sat):
    """Nevada y el ciclo de 5 estados que lo rodea impiden usar 3 colores."""
    colores = [f"C{i}" for i in range(n_colores)]
    entorno, asignacion = resolver(EEUU["regiones"], EEUU["adyacencias"], colores)
    assert (asignacion is not None) == sat
    if sat:
        coloreado = entorno.decodificar(asignacion)
        assert all(coloreado[a] != coloreado[b] for a, b in EEUU["adyacencias"])
