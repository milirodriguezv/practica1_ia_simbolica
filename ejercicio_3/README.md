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
python main.py                   # terrenos de ejemplo + rutas UCS/voraz/A* -> maps/*.npz, figures/*.png
pytest tests                     # tests
python run_experiments.py        # experimentos E1-E5 -> results/*.csv (~6 min; --rapido para probar, o p.ej. E2 E4)
python make_figures.py           # figuras -> figures/*.pdf|png, tablas -> results/tabla_*.tex
```

## Archivos

| Archivo | Qué contiene | Estado |
|---|---|---|
| `parametros.py` | Constantes físicas: `s`, `v_max`, `θ_max`, `k_sub`, `k_baj` | ✅ |
| `terrain.py` | Entorno: generador de terreno sintético + reglas de movimiento (`Terreno`) | ✅ |
| `visualizar_terreno.py` | Dibuja el mapa, las zonas prohibidas y las rutas | ✅ |
| `problem.py` | `RoverProblem`: formulación de búsqueda y modelo de coste `c = d / v(θ)` | ✅ |
| `heuristics.py` | `h0`, `h1` (euclídea), `h2` (octil) | ✅ |
| `search.py` | Primero-el-mejor genérica → UCS, voraz, A* | ✅ |
| `metrics.py` | Factor de ramificación efectivo `b*` | ✅ |
| `rover_agent.py` | Agente formular → buscar → ejecutar (replanifica si se desvía) | ✅ |
| `run_experiments.py` | Experimentos E1–E5 → `results/*.csv` | ✅ |
| `make_figures.py` | Figuras (`figures/*.pdf`) y tablas LaTeX (`results/tabla_*.tex`) de la memoria | ✅ |
| `tests/` | Tests con pytest (terreno, problema, búsqueda, agente) | ✅ |

Carpetas de salida: `maps/` (mapas `.npz` reproducibles), `results/` (CSV), `figures/` (imágenes).

## Reproducibilidad

Todos los mapas dependen de `(ParametrosGenerador, semilla)`; la misma pareja genera siempre el mismo terreno, `S` y `G`.
