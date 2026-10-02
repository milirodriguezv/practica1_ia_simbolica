# E6. Comprobacion de la subsuncion con platos aleatorios

10000 platos aleatorios (1-5 ingredientes atomicos, semilla 0), clasificados uno a uno con clasificar().

| C | D | Razonador: ¿C ⊑ D? | Platos en C | De ellos, fuera de D | ¿Coincide? |
|---|---|---|---|---|---|
| SinGluten | Vegetariano | No | 8861 | 4443 | Si |
| SinGluten | SinCarne | No | 8861 | 3189 | Si |
| SinGluten | SinLactosa | No | 8861 | 2814 | Si |
| SinGluten | Vegano | No | 8861 | 6299 | Si |
| Vegetariano | SinGluten | No | 5025 | 607 | Si |
| Vegetariano | SinCarne | Si | 5025 | 0 | Si |
| Vegetariano | SinLactosa | No | 5025 | 1639 | Si |
| Vegetariano | Vegano | No | 5025 | 2070 | Si |
| SinCarne | SinGluten | No | 6436 | 764 | Si |
| SinCarne | Vegetariano | No | 6436 | 1411 | Si |
| SinCarne | SinLactosa | No | 6436 | 2054 | Si |
| SinCarne | Vegano | No | 6436 | 3481 | Si |
| SinLactosa | SinGluten | No | 6865 | 818 | Si |
| SinLactosa | Vegetariano | No | 6865 | 3479 | Si |
| SinLactosa | SinCarne | No | 6865 | 2483 | Si |
| SinLactosa | Vegano | No | 6865 | 3910 | Si |
| Vegano | SinGluten | No | 2955 | 393 | Si |
| Vegano | Vegetariano | Si | 2955 | 0 | Si |
| Vegano | SinCarne | Si | 2955 | 0 | Si |
| Vegano | SinLactosa | Si | 2955 | 0 | Si |

Coinciden 20 de 20 parejas.
