# Permite que los tests importen los modulos de ejercicio_3 (terrain, problem...)
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from terrain import Terreno  # noqa: E402


@pytest.fixture
def mapa_4x4():
    """Ejemplo 4x4 resuelto a mano (memoria/ej3_fase1_heuristicas.tex,
    Bloque D): roca en (1, 2), S = (0, 0), G = (3, 3)."""
    alturas = np.array([[0.0, 0.1, 0.2, 0.3],
                        [0.2, 1.2, 0.6, 0.3],
                        [0.4, 0.5, 0.5, 0.2],
                        [0.5, 0.6, 0.3, 0.0]])
    rocas = np.zeros((4, 4), dtype=bool)
    rocas[1, 2] = True
    return Terreno(alturas, rocas, inicio=(0, 0), objetivo=(3, 3))
