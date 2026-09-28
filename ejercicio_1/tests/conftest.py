# Permite que los tests importen los modulos de ejercicio_1 (dpll_solver, environment...)
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
