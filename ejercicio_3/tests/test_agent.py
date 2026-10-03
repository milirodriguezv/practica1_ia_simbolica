"""Tests del agente: el ciclo formular -> buscar -> ejecutar
lleva al rover de S a G por la ruta que da la busqueda, y replanifica
si la posicion percibida no es la esperada."""

import numpy as np
from heuristics import h2
from main import simular
from rover_agent import RoverAgent
from search import astar_search
from terrain import Terreno

RUTA_OPTIMA_4X4 = [(0, 0), (1, 0), (2, 1), (3, 2), (3, 3)]


def test_agente_sigue_ruta_optima_4x4(mapa_4x4):
    agente = RoverAgent(astar_search, h2)
    assert simular(agente, mapa_4x4) == RUTA_OPTIMA_4X4
    assert agente.busquedas == 1  # sin sorpresas, planifica una sola vez


def test_sin_camino_no_se_mueve():
    rocas = np.zeros((4, 4), dtype=bool)
    rocas[2, 2:] = rocas[3, 2] = True  # G = (3, 3) encerrada
    terreno = Terreno(np.zeros((4, 4)), rocas, inicio=(0, 0), objetivo=(3, 3))
    agente = RoverAgent(astar_search, h2)
    assert simular(agente, terreno) == [(0, 0)]


def test_replanifica_si_se_desvia(mapa_4x4):
    agente = RoverAgent(astar_search, h2)
    G = mapa_4x4.objetivo
    assert agente((mapa_4x4, (0, 0), G)) == (1, 0)  # espera acabar en (1, 0)...
    agente((mapa_4x4, (0, 1), G))                   # ...pero ha patinado a (0, 1)
    assert agente.busquedas == 2
    assert agente.resultado.ruta[0] == (0, 1)
