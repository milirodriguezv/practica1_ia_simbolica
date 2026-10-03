# Ejercicio 2 — Ontología de una carta italiana y razonamiento sobre categorías

## Qué hace

A partir de los ingredientes de cada plato, el razonador **infiere** qué
restricciones alimentarias cumple (SinGluten, Vegetariano, SinCarne,
SinLactosa, Vegano). Ninguna categoría se asigna a mano, y la jerarquía
entre categorías (p. ej. Vegano ⊑ Vegetariano ⊑ SinCarne) tampoco: se infiere.

Tareas de lógica descriptiva implementadas:

| Tarea | Función | Nivel |
|---|---|---|
| Clasificación | `clasificar` | plato → categorías |
| Subsunción | `subsume`, `jerarquia_categorias` | categoría ⊑ categoría |
| Consistencia | `es_satisfacible` | ¿puede existir un plato así? |
| Validación de la ontología | `validar_ontologia` | disjunción, exhaustividad, ciclos |
| Auditoría de la carta | `auditar_carta` | etiquetas declaradas vs. inferidas |

## Ficheros

- `ontologia.py` — TBox: taxonomía de ingredientes y definición de las categorías.
- `carta.py` — ABox: ingredientes elaborados y los 9 platos de la carta.
- `razonador.py` — algoritmos (no contiene ningún plato ni ingrediente concreto).
- `main.py` — experimentos (validación, clasificación, subsunción, cambio del Pecorino, consistencia, auditoría y menús para clientes); guarda los resultados en `resultados/`.
- `test_razonador.py` — tests.

## Cómo ejecutar

```
python main.py            # todos los experimentos
python main.py auditoria  # un experimento concreto
python -m unittest test_razonador.py -v
```

## Supuestos

- **Mundo cerrado:** la lista de ingredientes de cada plato es completa.
- **Cierre del dominio:** los únicos ingredientes posibles son los declarados
  en la ontología; la subsunción es exacta respecto a ellos.
- **PlatoValido:** un plato sin ingredientes no pertenece a ninguna categoría
  (evita la verdad vacía del ∀).
- **Vegetariano** se define como "sin carne ni pescado". No se modela el
  cuajo animal de algunos quesos (p. ej. el Parmigiano Reggiano), que
  algunos vegetarianos estrictos no aceptan.
- Criterio de precaución con la lactosa: solo el Parmesano se considera
  sin lactosa (ver el experimento del cambio del Pecorino).
- La etiqueta "SinLactosa" del helado en `carta.py` es un error introducido
  a propósito para comprobar que la auditoría lo detecta.
