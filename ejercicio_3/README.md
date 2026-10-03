# Ejercicio 3: planificador de rutas para un rover en Marte con A*

Un rover tiene que ir de una celda S a otra G por un terreno con cráteres y
rocas, en el menor tiempo posible. El coste de cada paso es la distancia
recorrida entre la velocidad a esa pendiente, así que subir cuesta más que
bajar. El agente formula el problema, busca una ruta con A* y la ejecuta.

## Ejecución

Desde esta carpeta, con el entorno de la práctica activado (ver el README de la raíz):

```
python main.py              # dos terrenos de ejemplo y las rutas de UCS, voraz y A*; salida en maps/ y figures/
python run_experiments.py   # experimentos; resultados en results/ (unos minutos; --rapido para probar)
python make_figures.py      # figuras en figures/ y tablas en results/ a partir de los CSV
pytest tests                # tests
```

## Archivos

| Archivo | Contenido |
|---|---|
| `parametros.py` | Constantes físicas del rover |
| `terrain.py` | Entorno: generador de terreno sintético y reglas de movimiento |
| `problem.py` | Formulación del problema de búsqueda y modelo de coste |
| `heuristics.py` | Heurísticas `h0`, `h1` (euclídea) y `h2` (octil) |
| `search.py` | Búsqueda primero-el-mejor: UCS, voraz y A* |
| `metrics.py` | Factor de ramificación efectivo `b*` |
| `rover_agent.py` | Agente: formular, buscar y ejecutar; replanifica si se desvía |
| `visualizar_terreno.py` | Dibujo de los mapas y las rutas |
| `main.py` | Genera dos terrenos y dibuja las rutas de cada algoritmo |
| `run_experiments.py` | Experimentos |
| `make_figures.py` | Figuras y tablas a partir de los resultados |
| `tests/` | Tests del terreno, el problema, la búsqueda y el agente |

## Experimentos

| Experimento | Qué se mide | Salida |
|---|---|---|
| `heuristicas` | Nodos generados, expandidos y `b*` de UCS, A*(h1) y A*(h2) según la profundidad de la solución | `results/heuristicas.csv`, `figures/nodos_por_profundidad.pdf`, `results/tabla_b_estrella_*.tex` |
| `voraz` | Tiempo de viaje que pierde la búsqueda voraz frente a A* y nodos que se ahorra | `results/voraz.csv`, `figures/voraz.pdf` |
| `ida_y_vuelta` | Coste de ir de S a G frente a volver de G a S | `results/ida_y_vuelta.csv`, `figures/ida_y_vuelta.pdf` |
| `pendiente_maxima` | Si sigue habiendo ruta, y cuánto se alarga, cuando el rover aguanta menos pendiente | `results/pendiente_maxima.csv`, `figures/pendiente_maxima.pdf` |

## Reproducibilidad

Todos los mapas dependen de los parámetros del generador y de una semilla: la
misma pareja genera siempre el mismo terreno, S y G. Los experimentos usan
semillas fijas, así que volver a ejecutarlos da los mismos resultados salvo la
columna de tiempo.

## Código reutilizado

`search.py` se basa en `best_first_search` de
[aima-python](https://github.com/aimacode/aima-python).
