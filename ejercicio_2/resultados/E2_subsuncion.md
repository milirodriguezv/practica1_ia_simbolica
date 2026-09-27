# E2. Subsuncion entre categorias (comparando definiciones)

| C | D | ¿C ⊑ D? | Contraejemplo |
|---|---|---|---|
| SinGluten | Vegetariano | No | plato {Anchoa} |
| SinGluten | SinCarne | No | plato {Cerdo} |
| SinGluten | SinLactosa | No | plato {Burrata} |
| Vegetariano | SinGluten | No | plato {Espaguetis} |
| Vegetariano | SinCarne | Si | - |
| Vegetariano | SinLactosa | No | plato {Burrata} |
| SinCarne | SinGluten | No | plato {Espaguetis} |
| SinCarne | Vegetariano | No | plato {Anchoa} |
| SinCarne | SinLactosa | No | plato {Burrata} |
| SinLactosa | SinGluten | No | plato {Espaguetis} |
| SinLactosa | Vegetariano | No | plato {Anchoa} |
| SinLactosa | SinCarne | No | plato {Cerdo} |

Un contraejemplo {h} es un plato hipotetico con un solo ingrediente h que cumple C pero no D.

Subsunciones inferidas: Vegetariano ⊑ SinCarne
