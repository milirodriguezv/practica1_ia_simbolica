# Subsuncion entre categorias (comparando definiciones)

| C | D | ¿C ⊑ D? | Contraejemplo |
|---|---|---|---|
| SinGluten | Vegetariano | No | plato {Anchoa} |
| SinGluten | SinCarne | No | plato {Cerdo} |
| SinGluten | SinLactosa | No | plato {Burrata} |
| SinGluten | Vegano | No | plato {Anchoa} |
| Vegetariano | SinGluten | No | plato {Espaguetis} |
| Vegetariano | SinCarne | Si | - |
| Vegetariano | SinLactosa | No | plato {Burrata} |
| Vegetariano | Vegano | No | plato {Burrata} |
| SinCarne | SinGluten | No | plato {Espaguetis} |
| SinCarne | Vegetariano | No | plato {Anchoa} |
| SinCarne | SinLactosa | No | plato {Burrata} |
| SinCarne | Vegano | No | plato {Anchoa} |
| SinLactosa | SinGluten | No | plato {Espaguetis} |
| SinLactosa | Vegetariano | No | plato {Anchoa} |
| SinLactosa | SinCarne | No | plato {Cerdo} |
| SinLactosa | Vegano | No | plato {Anchoa} |
| Vegano | SinGluten | No | plato {Espaguetis} |
| Vegano | Vegetariano | Si | - |
| Vegano | SinCarne | Si | - |
| Vegano | SinLactosa | Si | - |

Un contraejemplo {h} es un plato hipotetico con un solo ingrediente h que cumple C pero no D.

Subsunciones inferidas: Vegetariano ⊑ SinCarne, Vegano ⊑ Vegetariano, Vegano ⊑ SinCarne, Vegano ⊑ SinLactosa
