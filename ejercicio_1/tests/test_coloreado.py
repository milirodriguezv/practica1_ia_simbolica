"""Tests del coloreado de mapas: la traduccion a clausulas, el entorno y
el agente completo (TELL -> ASK -> goal_test)."""

from environment import Environment
from logical_agent import LogicalAgent
from mapas import AUSTRALIA, EEUU, VECINOS_EEUU

REGIONES, ADYACENCIAS = AUSTRALIA["regiones"], AUSTRALIA["adyacencias"]
TRES_COLORES = ["Rojo", "Verde", "Azul"]


def resolver(mapa, colores):
    entorno = Environment(mapa["regiones"], mapa["adyacencias"], colores)
    asignacion = LogicalAgent().run(entorno)
    return entorno, asignacion


def test_numero_de_variables_y_clausulas():
    """Australia con 3 colores: 7 * 3 = 21 variables y
    7 (al menos un color) + 7 * 3 (a lo sumo uno) + 9 * 3 (vecinos) = 55 clausulas."""
    entorno = Environment(REGIONES, ADYACENCIAS, TRES_COLORES)
    assert len(entorno.variable_id) == 21
    assert len(entorno.traducir_a_clausulas()) == 55


def test_australia_con_3_colores():
    entorno, asignacion = resolver(AUSTRALIA, TRES_COLORES)
    assert asignacion is not None
    coloreado = entorno.decodificar(asignacion)
    assert set(coloreado) == set(REGIONES)
    for a, b in ADYACENCIAS:
        assert coloreado[a] != coloreado[b]


def test_australia_con_2_colores_es_unsat():
    """WA, NT y SA son vecinas entre si: hacen falta 3 colores."""
    _, asignacion = resolver(AUSTRALIA, ["Rojo", "Verde"])
    assert asignacion is None


def test_goal_test_rechaza_vecinos_del_mismo_color():
    entorno = Environment(REGIONES, ADYACENCIAS, TRES_COLORES)
    todo_rojo = {entorno.variable_id[(r, "Rojo")]: True for r in REGIONES}
    assert not entorno.goal_test(todo_rojo)


def test_mapa_de_eeuu_bien_escrito():
    """48 estados, 105 fronteras y cada frontera apuntada en los dos estados."""
    assert len(EEUU["regiones"]) == 48
    assert len(EEUU["adyacencias"]) == 105
    for estado, vecinos in VECINOS_EEUU.items():
        for vecino in vecinos:
            assert estado in VECINOS_EEUU[vecino], f"{estado}-{vecino} solo en un sentido"


def test_eeuu_necesita_4_colores():
    _, con_tres = resolver(EEUU, TRES_COLORES)
    assert con_tres is None

    entorno, con_cuatro = resolver(EEUU, TRES_COLORES + ["Amarillo"])
    coloreado = entorno.decodificar(con_cuatro)
    for a, b in EEUU["adyacencias"]:
        assert coloreado[a] != coloreado[b]
