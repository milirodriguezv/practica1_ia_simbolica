"""Tests del agente (paso 4): el ciclo formular -> buscar -> ejecutar
lleva al rover de S a G por la ruta que da la busqueda, y replanifica
si la posicion percibida no es la esperada."""

import numpy as np
from heuristics import h2
from main import simular
from rover_agent import RoverAgent
from search import astar_search, greedy_search, uniform_cost_search
from terrain import Terreno

RUTA_OPTIMA_4X4 = [(0, 0), (1, 0), (2, 1), (3, 2), (3, 3)]


def test_agente_sigue_ruta_optima_4x4(mapa_4x4):
    for algoritmo, h in [(uniform_cost_search, None), (astar_search, h2)]:
        agente = RoverAgent(algoritmo, h)
        assert simular(agente, mapa_4x4) == RUTA_OPTIMA_4X4
        assert agente.busquedas == 1  # sin sorpresas, planifica una sola vez


def test_agente_voraz_llega_a_g(mapa_4x4):
    agente = RoverAgent(greedy_search, h2)
    recorrido = simular(agente, mapa_4x4)
    assert recorrido == agente.resultado.ruta
    assert recorrido[-1] == mapa_4x4.objetivo


def test_plan_son_acciones_de_la_ruta(mapa_4x4):
    agente = RoverAgent(astar_search, h2)
    problema = agente.formular(mapa_4x4, mapa_4x4.inicio, mapa_4x4.objetivo)
    plan = agente.buscar(problema)
    assert plan == [(1, 0), (1, 1), (1, 1), (0, 1)]


def test_en_objetivo_no_actua(mapa_4x4):
    agente = RoverAgent(astar_search, h2)
    assert agente((mapa_4x4, mapa_4x4.objetivo, mapa_4x4.objetivo)) is None
    assert agente.busquedas == 0


def test_sin_camino_devuelve_none():
    rocas = np.zeros((4, 4), dtype=bool)
    rocas[2, 2:] = rocas[3, 2] = True  # G = (3, 3) encerrada
    terreno = Terreno(np.zeros((4, 4)), rocas, inicio=(0, 0), objetivo=(3, 3))
    agente = RoverAgent(astar_search, h2)
    assert simular(agente, terreno) == [(0, 0)]
    assert agente.resultado.ruta is None


def test_replanifica_si_se_desvia(mapa_4x4):
    agente = RoverAgent(astar_search, h2)
    G = mapa_4x4.objetivo
    assert agente((mapa_4x4, (0, 0), G)) == (1, 0)  # espera acabar en (1, 0)...
    accion = agente((mapa_4x4, (0, 1), G))  # ...pero ha patinado a (0, 1)
    assert agente.busquedas == 2
    assert agente.resultado.ruta[0] == (0, 1)
    siguiente = agente.resultado.ruta[1]
    assert accion == (siguiente[0] - 0, siguiente[1] - 1)
