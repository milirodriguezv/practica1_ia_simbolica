# E1. Clasificacion de la carta

| Plato | Tipo | SinGluten | Vegetariano | SinCarne | SinLactosa |
|---|---|---|---|---|---|
| VitelTone | Entrante | ✓ | ✗ | ✗ | ✓ |
| BurrataConTomatesConfitados | Entrante | ✓ | ✓ | ✓ | ✗ |
| PizzaMozzarella | Principal | ✗ | ✓ | ✓ | ✗ |
| PastaCarbonara | Principal | ✗ | ✗ | ✗ | ✗ |
| EnsaladaRuculaPeraParmesano | Principal | ✓ | ✓ | ✓ | ✓ |
| SalmonConVerdurasAlHorno | Principal | ✓ | ✗ | ✓ | ✓ |
| Tiramisu | Postre | ✗ | ✓ | ✓ | ✗ |
| HeladoDePistacho | Postre | ✓ | ✓ | ✓ | ✗ |

## Justificaciones (por que NO cumple)

- VitelTone no es Vegetariano: Ternera (VitelTone) es Carne
- VitelTone no es Vegetariano: Atun (VitelTone -> SalsaTonnata) es Pescado
- VitelTone no es Vegetariano: Anchoa (VitelTone -> SalsaTonnata) es Pescado
- VitelTone no es SinCarne: Ternera (VitelTone) es Carne
- BurrataConTomatesConfitados no es SinLactosa: Burrata (BurrataConTomatesConfitados) es ConLactosa
- PizzaMozzarella no es SinGluten: HarinaTrigo (PizzaMozzarella -> MasaPizza) es ConGluten
- PizzaMozzarella no es SinLactosa: Mozzarella (PizzaMozzarella) es ConLactosa
- PastaCarbonara no es SinGluten: Espaguetis (PastaCarbonara) es ConGluten
- PastaCarbonara no es Vegetariano: Guanciale (PastaCarbonara) es Carne
- PastaCarbonara no es SinCarne: Guanciale (PastaCarbonara) es Carne
- PastaCarbonara no es SinLactosa: PecorinoRomano (PastaCarbonara) es ConLactosa
- SalmonConVerdurasAlHorno no es Vegetariano: Salmon (SalmonConVerdurasAlHorno) es Pescado
- Tiramisu no es SinGluten: HarinaTrigo (Tiramisu -> Bizcochos) es ConGluten
- Tiramisu no es SinLactosa: Mascarpone (Tiramisu -> CremaMascarpone) es ConLactosa
- HeladoDePistacho no es SinLactosa: Leche (HeladoDePistacho -> BaseHelado) es ConLactosa
- HeladoDePistacho no es SinLactosa: Nata (HeladoDePistacho -> BaseHelado) es ConLactosa
