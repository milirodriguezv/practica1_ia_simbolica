# Ejercicio 2: ontología de una carta italiana y razonamiento sobre categorías

A partir de los ingredientes de cada plato, el razonador infiere qué
restricciones alimentarias cumple (SinGluten, Vegetariano, SinCarne, SinLactosa,
Vegano). Ninguna categoría se asigna a mano, y la jerarquía entre categorías
(por ejemplo, Vegano ⊑ Vegetariano ⊑ SinCarne) tampoco: se infiere de sus
definiciones.

## Ejecución

Desde esta carpeta, con el entorno de la práctica activado (ver el README de la raíz):

```
python main.py                         # todos los experimentos; resultados en resultados/
python main.py auditoria               # un experimento concreto
python -m unittest test_razonador.py   # tests
```

## Archivos

| Archivo | Contenido |
|---|---|
| `ontologia.py` | TBox: taxonomía de ingredientes y definición de las categorías |
| `carta.py` | ABox: ingredientes elaborados y los 9 platos de la carta |
| `razonador.py` | Algoritmos de razonamiento; no contiene ningún plato ni ingrediente concreto |
| `main.py` | Experimentos |
| `test_razonador.py` | Tests del razonador |

## Experimentos

| Experimento | Qué se hace | Salida |
|---|---|---|
| `validacion` | Comprueba la ontología y la carta antes de razonar (se ejecuta siempre) | `resultados/validacion.md` |
| `clasificacion` | Categorías que cumple cada plato, con la justificación de las que no | `resultados/clasificacion.md` |
| `subsuncion` | Qué categorías están contenidas en otras, comparando sus definiciones | `resultados/subsuncion.md` |
| `comprobacion_subsuncion` | Contrasta la subsunción clasificando los 50 platos de un solo ingrediente | `resultados/comprobacion_subsuncion.md` |
| `cambio_del_pecorino` | Efecto de cambiar un axioma de la TBox sin tocar la carta | `resultados/cambio_del_pecorino.md` |
| `consistencia` | Si puede existir un plato con ciertas combinaciones | `resultados/consistencia.md` |
| `auditoria` | Etiquetas impresas en la carta frente a lo inferido | `resultados/auditoria.md`, `resultados/auditoria.pdf` |
| `menus_para_clientes` | Qué entrante, principal y postre puede pedir cada tipo de cliente | `resultados/menus_para_clientes.md` |

## Supuestos

- Mundo cerrado: la lista de ingredientes de cada plato es completa.
- Cierre del dominio: los únicos ingredientes posibles son los declarados en la
  ontología; la subsunción es exacta respecto a ellos.
- Un plato sin ingredientes no pertenece a ninguna categoría (PlatoValido), para
  evitar la verdad vacía del cuantificador universal.
- Vegetariano se define como "sin carne ni pescado". No se modela el cuajo
  animal de algunos quesos, como el Parmigiano Reggiano.
- Criterio de precaución con la lactosa: solo el Parmesano se considera sin
  lactosa (ver el experimento `cambio_del_pecorino`).
- La etiqueta "SinLactosa" del helado en `carta.py` es un error introducido a
  propósito para comprobar que la auditoría lo detecta.
