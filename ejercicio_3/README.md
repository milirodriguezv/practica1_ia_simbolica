# Ejercicio 3 — Planificador de rutas para un rover en Marte con A*

## Instalación

```bash
cd practica1_ia_simbolica
python -m venv .venv
.venv\Scripts\activate          # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt # requirements.txt común a toda la práctica
cd ejercicio_3                  # los comandos de abajo se ejecutan desde aquí
```

## Ejecución

```bash
python main.py                   # genera terrenos de ejemplo -> maps/*.npz y figures/*.png
pytest tests                     # tests
python run_experiments.py        # (paso 5) experimentos E1-E5 -> results/*.csv
python make_figures.py           # (paso 5) figuras de la memoria -> figures/*.pdf
```

## Archivos

| Archivo | Qué contiene | Estado |
|---|---|---|
| `parametros.py` | Constantes físicas: `s`, `v_max`, `θ_max`, `k_sub`, `k_baj` | ✅ |
| `terrain.py` | Entorno: generador de terreno sintético + reglas de movimiento (`Terreno`) | ✅ |
| `visualizar_terreno.py` | Dibuja el mapa, las zonas prohibidas y las rutas | ✅ |
| `problem.py` | `RoverProblem`: formulación de búsqueda y modelo de coste `c = d / v(θ)` | ⏳ paso 3 |
| `heuristics.py` | `h0`, `h1` (euclídea), `h2` (octil), ponderada | ⏳ paso 3 |
| `search.py` | Primero-el-mejor genérica → UCS, voraz, A* | ⏳ paso 3 |
| `metrics.py` | Factor de ramificación efectivo `b*` | ⏳ paso 3 |
| `rover_agent.py` | Agente formular → buscar → ejecutar | ⏳ paso 4 |
| `run_experiments.py` / `make_figures.py` | Experimentos E1–E5 y figuras | ⏳ paso 5 |
| `tests/` | Tests con pytest | terreno ✅ |

Carpetas de salida: `maps/` (mapas `.npz` reproducibles), `results/` (CSV), `figures/` (imágenes).

## Reproducibilidad

Todos los mapas dependen de `(ParametrosGenerador, semilla)`; la misma pareja genera siempre el mismo terreno, `S` y `G`.
