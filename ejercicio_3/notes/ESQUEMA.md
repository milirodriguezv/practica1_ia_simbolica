# Esquema del Ejercicio 3 — Rover en Marte con A*

Mapa de la carpeta: **en qué orden leer los archivos**, **para qué sirve cada
uno** y **qué hace cada función** y cómo se relacionan.
Para el detalle paso a paso de cómo funciona cada función, ver
[NOTAS_IMPLEMENTACION.md](NOTAS_IMPLEMENTACION.md).

Leyenda: ✅ implementado · ⏳ pendiente (solo esqueleto)

---

## 1. Árbol de la carpeta (en orden de lectura)

```
ejercicio_3/
│
├── 1.  parametros.py           ✅ constantes físicas del rover
├── 2.  terrain.py              ✅ EL ENTORNO: genera el mapa y dice qué movimientos son posibles
├── 3.  visualizar_terreno.py   ✅ dibuja mapas y rutas
├── 4.  problem.py              ✅ EL PROBLEMA: formulación de búsqueda + coste (tiempo)
├── 5.  heuristics.py           ✅ h0, h1, h2 (estimaciones del tiempo que falta)
├── 6.  search.py               ⏳ EL ALGORITMO: UCS, voraz y A* (un solo código)
├── 7.  metrics.py              ⏳ factor de ramificación efectivo b*
├── 8.  rover_agent.py          ⏳ EL AGENTE: formular → buscar → ejecutar
├── 9.  main.py                 ✅ demo: lo junta todo (ahora solo el paso 1)
├── 10. run_experiments.py      ⏳ experimentos E1–E5 → results/*.csv
├── 11. make_figures.py         ⏳ figuras de la memoria → figures/*.pdf
│
├── tests/
│   ├── conftest.py             ✅ path de los módulos + mapa 4×4 de la memoria (fixture)
│   ├── test_terrain.py         ✅ 8 tests del terreno
│   └── test_problem.py         ✅ 10 tests de coste y heurísticas
│
├── memoria/
│   └── ej3_fase1_heuristicas.tex   ✅ heurísticas + demostraciones + ejemplo 4×4 (datos de test)
│
├── notes/
│   ├── ESQUEMA.md                  este archivo
│   └── NOTAS_IMPLEMENTACION.md     explicación detallada de cada función
│
├── maps/                       mapas guardados (.npz), reproducibles
├── results/                    CSV de los experimentos
├── figures/                    imágenes (.png / .pdf)
│
└── README.md                   instalación y cómo ejecutar

(requirements.txt está en practica1_ia_simbolica/, común a los 3 ejercicios)
```

El orden sigue las **dependencias**: cada archivo solo usa los que tiene por encima.

---

## 2. Cómo se relacionan (quién usa a quién)

```
                    parametros.py
                   (constantes físicas)
                 ┌────────┼─────────┐
                 ▼        ▼         ▼
           terrain.py  problem.py  heuristics.py
           (el mundo)  (el coste)  (estimaciones)
                 │        ▲  │         │
                 └────────┘  │         │
                  Terreno    ▼         ▼
                           search.py ◄─┘         metrics.py
                          (UCS/voraz/A*)          (b*)
                              │                     │
                              ▼                     │
                        rover_agent.py              │
                     (formular→buscar→ejecutar)     │
                              │                     │
          ┌───────────────────┼─────────────────────┤
          ▼                   ▼                     ▼
       main.py        run_experiments.py ──► make_figures.py
          │                   │                     │
          └───────► visualizar_terreno.py ◄─────────┘
```

**Flujo de datos de una ejecución:**

```
semilla ──► generar_terreno() ──► Terreno ──► RoverProblem ──► astar_search(h2) ──► ResultadoBusqueda
                                    │                                                  (ruta, coste,
                                    └──────────────► dibujar_terreno(rutas) ◄───────── nodos, tiempo)
```


## 3. Archivo por archivo

### 1. `parametros.py` ✅
**Objetivo:** tener todas las constantes físicas en un único sitio. Si se cambia
una, cambia en todo el ejercicio.

| Constante | Valor | Para qué |
|---|---|---|
| `S_CELL` | 1 m | Tamaño de celda |
| `V_MAX` | 0,042 m/s | Velocidad máxima (coste y heurísticas) |
| `THETA_MAX` | 25° | Pendiente máxima permitida |
| `K_SUB`, `K_BAJ` | 0,8 / 0,4 | Cuánto se frena al subir / bajar |
| `DIRECCIONES` | 8 pares `(di, dj)` | Los 8 movimientos posibles |

**Lo usan:** `terrain.py`, `problem.py`, `heuristics.py`.

---

### 2. `terrain.py` ✅ — el entorno
**Objetivo:** fabricar el trozo de Marte (alturas + rocas + S + G) y decir qué
movimientos son **físicamente posibles**. No sabe nada de costes ni de búsqueda.

**a) Generador (capas del mapa)**

| Función | Objetivo |
|---|---|
| `ParametrosGenerador` | "Receta" del mapa: tamaño, nº de cráteres, densidad de rocas… (controles de dificultad) |
| `generar_relieve_base(rng, N, sigma, amplitud)` | Capa 1: suelo ondulado (ruido + filtro gaussiano), ±1 m |
| `altura_crater(r, radio, profundidad, eta, w)` | Forma de UN cráter: cuánto hundir/levantar según la distancia al centro |
| `generar_crateres(rng, N, s, p)` | Capa 2: elige dónde y de qué tamaño es cada cráter y usa `altura_crater` para excavarlo |
| `generar_rocas(rng, N, p)` | Capa 3: máscara sí/no de rocas (discos de 1–2 celdas) |

**b) La clase `Terreno` (el mundo ya construido)**

| Método | Objetivo |
|---|---|
| `__init__(alturas, rocas, …)` | Guarda el mapa y precalcula la tabla de movimientos factibles |
| `N` | Tamaño del mapa |
| `dentro(celda)` | ¿La celda está dentro del mapa? |
| `es_transitable(celda)` | ¿Dentro y sin roca? |
| `distancia_horizontal(di, dj)` | 1 m (recto) o 1,41 m (diagonal) |
| `pendiente(a, b)` | Pendiente con signo del paso a → b (+ sube, − baja) |
| `_desplazar(...)` *(función auxiliar, fuera de la clase)* | Da "lo que tiene la vecina" de todas las celdas a la vez |
| `_calcular_factibilidad()` | Aplica las 4 reglas (dentro, sin rocas, ≤ 25°, esquinas) en las 8 direcciones y crea la tabla |
| `es_movimiento_factible(celda, di, dj)` | Consulta la tabla para UN paso |
| `movimientos_factibles(celda)` | Lista de pasos `(di, dj)` posibles → **lo usará `problem.actions`** |
| `vecinos_factibles(celda)` | Lo mismo, pero devuelve las celdas destino |
| `alcanzables_desde(origen)` | BFS: todas las celdas a las que se puede llegar (sin mirar el coste) |
| `mascara_pendiente_excesiva()` | Celdas con alguna pared > 25° (solo para pintarlas en rojo) |
| `resumen()` | Texto con los datos del mapa |

**c) Instancias completas y ficheros**

| Función | Objetivo |
|---|---|
| `elegir_inicio_objetivo(terreno, rng, separacion_min)` | Elige S y G transitables, lejos entre sí y conectados (usa `alcanzables_desde`) |
| `generar_terreno(params, semilla)` | **Función principal:** capas → `Terreno` → S y G; si no hay camino, regenera |
| `guardar_terreno(terreno, ruta, params)` | Guarda en `maps/*.npz` |
| `cargar_terreno(ruta)` | Lee un `.npz` y reconstruye el `Terreno` |

**Cadena de llamadas:**
```
generar_terreno
 ├── generar_relieve_base
 ├── generar_crateres ──► altura_crater (×12)
 ├── generar_rocas
 ├── Terreno(...) ──► _calcular_factibilidad ──► _desplazar
 └── elegir_inicio_objetivo ──► alcanzables_desde ──► vecinos_factibles
```

---

### 3. `visualizar_terreno.py` ✅
**Objetivo:** dibujar. Sin lógica de búsqueda.

| Función | Objetivo |
|---|---|
| `dibujar_terreno(terreno, titulo, nombre_archivo, rutas=None)` | Mapa de alturas + paredes > 25° en rojo + rocas + S y G + rutas opcionales (`{"A*": [...], ...}`). Guarda en `figures/` |

**Usa:** `Terreno.mascara_pendiente_excesiva`. **Lo usan:** `main.py`, `make_figures.py`.

---

### 4. `problem.py` ✅ — el problema de búsqueda
**Objetivo:** traducir el terreno a un **problema de búsqueda** (interfaz del
libro / aima-python) y definir el **coste = tiempo**. Aquí aparece la asimetría.

| Función / método | Objetivo |
|---|---|
| `velocidad(theta)` | v(θ): más lenta al subir (hasta 0,2·v_max) que al bajar (hasta 0,6·v_max), nunca > v_max |
| `RoverProblem(terreno, inicio, objetivo)` | Guarda el terreno, S (`initial`) y G (`goal`) |
| `actions(estado)` | Pasos posibles, que pide a `terreno.movimientos_factibles` |
| `result(estado, accion)` | `(i + di, j + dj)` |
| `is_goal(estado)` | `estado == G` |
| `action_cost(estado, accion, siguiente)` | Tiempo del paso: `d / v(θ)` |

**Usa:** `Terreno`, `parametros`. **Lo usan:** `search.py`, `heuristics.py`, `rover_agent.py`.

---

### 5. `heuristics.py` ✅ — estimaciones
**Objetivo:** estimar "cuánto tiempo falta hasta G" sin pasarse nunca
(admisibles), obtenidas por **relajación**.

| Función | Objetivo |
|---|---|
| `h0` | Siempre 0 → A* se convierte en UCS (línea base) |
| `h1` | Distancia en línea recta / v_max |
| `h2` | Distancia octil (8 direcciones) / v_max. Domina a h1 |
| `ponderada(h, w)` | `w · h`, para A* ponderado (no admisible si w > 1) |

**Firma común:** `h(estado, problema)`, que usa `problema.goal` y `problema.terreno.s`.
**Lo usan:** `search.py`.

---

### 6. `search.py` ⏳ — el algoritmo
**Objetivo:** **una sola** búsqueda primero-el-mejor; los algoritmos se obtienen
cambiando `f`.

| Función / clase | Objetivo |
|---|---|
| `ResultadoBusqueda` | Todo lo que devuelve una búsqueda: ruta, coste, nodos generados/expandidos, frontera máx., tiempo, orden de expansión |
| `ResultadoBusqueda.profundidad` | Nº de pasos de la ruta (`d`, para b*) |
| `best_first_search(problema, f, h)` | ⏳ El motor: cola de prioridad por `f`, test objetivo al expandir, contadores |
| `uniform_cost_search(problema)` | ⏳ `f = g` |
| `greedy_search(problema, h)` | ⏳ `f = h` |
| `astar_search(problema, h, w=1)` | ⏳ `f = g + w·h` |

```
uniform_cost_search ─┐
greedy_search ───────┼──► best_first_search ──► problema.actions / result / action_cost / is_goal
astar_search ────────┘                     └──► h(estado, problema)
```
**Lo usan:** `rover_agent.py`, `run_experiments.py`, `main.py`.

---

### 7. `metrics.py` ⏳
**Objetivo:** calcular métricas para comparar algoritmos (tabla estilo fig. 3.26).

| Función | Objetivo |
|---|---|
| `factor_ramificacion_efectivo(nodos_generados, profundidad)` | ⏳ b* por bisección: cuanto más cerca de 1, mejor heurística |

**Usa:** datos de `ResultadoBusqueda`. **Lo usan:** `run_experiments.py`.

---

### 8. `rover_agent.py` ⏳ — el agente
**Objetivo:** el ciclo del agente basado en objetivos: si no tiene plan,
**formula** el problema y **busca**; luego **ejecuta** acción a acción.

| Método | Objetivo |
|---|---|
| `RoverAgent(algoritmo, heuristica)` | Elige con qué algoritmo y heurística planifica |
| `formular(terreno, posicion, objetivo)` | ⏳ Crea un `RoverProblem` |
| `buscar(problema)` | ⏳ Llama al algoritmo y guarda el plan |
| `__call__(percepcion)` | ⏳ Devuelve la siguiente acción del plan (replanifica si hace falta) |

**Usa:** `problem.py`, `search.py`, `heuristics.py`. **Lo usan:** `main.py`.

---

### 9. `main.py` ✅ (parcial)
**Objetivo:** demo que se ejecuta con `python main.py`.

| Función | Objetivo |
|---|---|
| `generar_y_dibujar(N, semilla)` | Genera un terreno, lo guarda en `maps/` y lo dibuja en `figures/`. Pendiente: planificar con el agente y dibujar las rutas |

---

### 10. `run_experiments.py` ⏳
**Objetivo:** ejecutar E1–E5 sobre muchos mapas con semilla fija y guardar CSV.

| Experimento | Qué mide |
|---|---|
| E1 | Corrección: coste A* = UCS = networkx |
| E2 | Nodos generados y b* de UCS, A*(h1), A*(h2) |
| E3 | Sobrecoste de la voraz frente a A* |
| E4 | Asimetría: ida frente a vuelta |
| E5 | Escalabilidad con N |

### 11. `make_figures.py` ⏳
**Objetivo:** leer `results/*.csv` y generar las figuras de la memoria.

---

### `tests/`
| Archivo | Objetivo |
|---|---|
| `conftest.py` | Añade `ejercicio_3/` al path y define la fixture `mapa_4x4` (ejemplo de la memoria) |
| `test_problem.py` | ✅ Lema 1 (velocidad), costes y asimetría del 4×4, coste mínimo, admisibilidad, consistencia, dominancia, ponderada |
| `test_terrain.py` | ✅ Reproducibilidad, S/G válidos, factibilidad = reglas, simetría, esquinas, límite de 25°, pared `arctan(4ρ)`, guardar/cargar |
| *(futuro)* `test_search.py` | ⏳ Mapa 4×4 a mano, A* = UCS = networkx, admisibilidad y consistencia |

---

## 4. Orden de implementación (fases)

| Paso | Archivos | Estado |
|---|---|---|
| 1 | `parametros.py`, `terrain.py`, `visualizar_terreno.py`, `test_terrain.py` | ✅ |
| 1b | Formalización en papel: `memoria/ej3_fase1_heuristicas.tex` | ✅ |
| 2 | `problem.py` (coste), `heuristics.py`, `test_problem.py` | ✅ |
| 3 | `search.py`, `metrics.py` + `test_search.py` | ⏳ siguiente |
| 4 | `rover_agent.py`, completar `main.py` | ⏳ |
| 5 | `run_experiments.py`, `make_figures.py` | ⏳ |
| 6 | Añadidos: A* ponderado, IDA*, replanificación | opcional |
