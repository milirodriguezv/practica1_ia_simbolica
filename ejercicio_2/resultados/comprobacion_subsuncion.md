# Comprobacion de la subsuncion con platos de un solo ingrediente

Se clasifican los 50 platos de un unico ingrediente atomico.

| C | D | Razonador: ¿C ⊑ D? | Platos en C | De ellos, fuera de D | ¿Coincide? |
|---|---|---|---|---|---|
| SinGluten | Vegetariano | No | 48 | 11 | Si |
| SinGluten | SinCarne | No | 48 | 7 | Si |
| SinGluten | SinLactosa | No | 48 | 6 | Si |
| SinGluten | Vegano | No | 48 | 19 | Si |
| Vegetariano | SinGluten | No | 39 | 2 | Si |
| Vegetariano | SinCarne | Si | 39 | 0 | Si |
| Vegetariano | SinLactosa | No | 39 | 6 | Si |
| Vegetariano | Vegano | No | 39 | 8 | Si |
| SinCarne | SinGluten | No | 43 | 2 | Si |
| SinCarne | Vegetariano | No | 43 | 4 | Si |
| SinCarne | SinLactosa | No | 43 | 6 | Si |
| SinCarne | Vegano | No | 43 | 12 | Si |
| SinLactosa | SinGluten | No | 44 | 2 | Si |
| SinLactosa | Vegetariano | No | 44 | 11 | Si |
| SinLactosa | SinCarne | No | 44 | 7 | Si |
| SinLactosa | Vegano | No | 44 | 13 | Si |
| Vegano | SinGluten | No | 31 | 2 | Si |
| Vegano | Vegetariano | Si | 31 | 0 | Si |
| Vegano | SinCarne | Si | 31 | 0 | Si |
| Vegano | SinLactosa | Si | 31 | 0 | Si |

Coinciden 20 de 20 parejas.
