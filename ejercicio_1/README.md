# Ejercicio 1: coloreado de mapas con un agente lógico y DPLL

El entorno es un mapa (regiones y fronteras) y un número de colores. El agente
traduce el mapa a cláusulas en forma normal conjuntiva, las anota en su base de
conocimiento (TELL) y pregunta si existe un coloreado válido (ASK). La respuesta
la calcula un SAT solver DPLL.

Se usan dos mapas: Australia (7 regiones) y los 48 estados contiguos de EE. UU.

## Ejecución

Desde esta carpeta, con el entorno de la práctica activado (ver el README de la raíz):

```
python main.py           # colorea los dos mapas y guarda las imágenes en figures/
python experimentos.py   # experimentos; resultados en results/ y figures/ (unos 3 minutos)
pytest tests             # tests
```

## Archivos

| Archivo | Contenido |
|---|---|
| `mapas.py` | Datos de los mapas: regiones, fronteras y posiciones para dibujar |
| `environment.py` | Entorno: el mapa y su traducción a cláusulas |
| `graph_coloring.py` | Funciones que generan las variables y las cláusulas FNC |
| `knowledge_base.py` | Base de conocimiento con las operaciones TELL y ASK |
| `logical_agent.py` | Agente basado en conocimiento |
| `dpll_solver.py` | Algoritmo DPLL, con contadores y reglas que se pueden desactivar |
| `visualizar_mapa.py` | Dibujo de los mapas coloreados |
| `main.py` | Resuelve los dos mapas y los dibuja |
| `experimentos.py` | Experimentos sobre los dos mapas |
| `tests/` | Tests del solver y del coloreado |

## Experimentos

| Experimento | Qué se mide | Salida |
|---|---|---|
| `numero_cromatico` | Menor número de colores con el que se puede pintar cada mapa | `results/numero_cromatico.csv` |
| `reglas_de_dpll` | Llamadas recursivas con y sin cláusula unitaria y símbolo puro | `results/reglas_dpll.csv`, `figures/reglas_dpll.pdf` |
| `estados_conflictivos` | Estados que impiden pintar EE. UU. con 3 colores | `results/estados_conflictivos.csv`, `figures/estados_conflictivos.pdf` |
| `fuerza_bruta` | Comprobación en Australia: coloreados válidos y modelos de la fórmula contados uno a uno, frente a la respuesta del agente | `results/fuerza_bruta.csv` |
