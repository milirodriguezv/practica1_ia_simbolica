# Clasificacion de la carta

| Plato | Tipo | SinGluten | Vegetariano | SinCarne | SinLactosa | Vegano |
|---|---|---|---|---|---|---|
| VitelTone | Entrante | ✓ | ✗ | ✗ | ✓ | ✗ |
| BurrataConTomatesConfitados | Entrante | ✓ | ✓ | ✓ | ✗ | ✗ |
| PizzaMozzarella | Principal | ✗ | ✓ | ✓ | ✗ | ✗ |
| EspaguetisAlPomodoro | Principal | ✗ | ✓ | ✓ | ✓ | ✓ |
| PastaCarbonara | Principal | ✗ | ✗ | ✗ | ✗ | ✗ |
| EnsaladaRuculaPeraParmesano | Principal | ✓ | ✓ | ✓ | ✓ | ✗ |
| SalmonConVerdurasAlHorno | Principal | ✓ | ✗ | ✓ | ✓ | ✗ |
| Tiramisu | Postre | ✗ | ✓ | ✓ | ✗ | ✗ |
| HeladoDePistacho | Postre | ✓ | ✓ | ✓ | ✗ | ✗ |

## Justificaciones (por que NO cumple)

- VitelTone no es Vegetariano: Ternera (VitelTone) es Carne
- VitelTone no es Vegetariano: Atun (VitelTone -> SalsaTonnata) es Pescado
- VitelTone no es Vegetariano: Anchoa (VitelTone -> SalsaTonnata) es Pescado
- VitelTone no es SinCarne: Ternera (VitelTone) es Carne
- VitelTone no es Vegano: Ternera (VitelTone) es IngAnimal
- VitelTone no es Vegano: Atun (VitelTone -> SalsaTonnata) es IngAnimal
- VitelTone no es Vegano: Anchoa (VitelTone -> SalsaTonnata) es IngAnimal
- VitelTone no es Vegano: HuevoGallina (VitelTone -> SalsaTonnata -> Mayonesa) es IngAnimal
- BurrataConTomatesConfitados no es SinLactosa: Burrata (BurrataConTomatesConfitados) es ConLactosa
- BurrataConTomatesConfitados no es Vegano: Burrata (BurrataConTomatesConfitados) es IngAnimal
- PizzaMozzarella no es SinGluten: HarinaTrigo (PizzaMozzarella -> MasaPizza) es ConGluten
- PizzaMozzarella no es SinLactosa: Mozzarella (PizzaMozzarella) es ConLactosa
- PizzaMozzarella no es Vegano: Mozzarella (PizzaMozzarella) es IngAnimal
- EspaguetisAlPomodoro no es SinGluten: Espaguetis (EspaguetisAlPomodoro) es ConGluten
- PastaCarbonara no es SinGluten: Espaguetis (PastaCarbonara) es ConGluten
- PastaCarbonara no es Vegetariano: Guanciale (PastaCarbonara) es Carne
- PastaCarbonara no es SinCarne: Guanciale (PastaCarbonara) es Carne
- PastaCarbonara no es SinLactosa: PecorinoRomano (PastaCarbonara) es ConLactosa
- PastaCarbonara no es Vegano: Guanciale (PastaCarbonara) es IngAnimal
- PastaCarbonara no es Vegano: HuevoGallina (PastaCarbonara) es IngAnimal
- PastaCarbonara no es Vegano: PecorinoRomano (PastaCarbonara) es IngAnimal
- EnsaladaRuculaPeraParmesano no es Vegano: Parmesano (EnsaladaRuculaPeraParmesano) es IngAnimal
- SalmonConVerdurasAlHorno no es Vegetariano: Salmon (SalmonConVerdurasAlHorno) es Pescado
- SalmonConVerdurasAlHorno no es Vegano: Salmon (SalmonConVerdurasAlHorno) es IngAnimal
- Tiramisu no es SinGluten: HarinaTrigo (Tiramisu -> Bizcochos) es ConGluten
- Tiramisu no es SinLactosa: Mascarpone (Tiramisu -> CremaMascarpone) es ConLactosa
- Tiramisu no es Vegano: HuevoGallina (Tiramisu -> Bizcochos) es IngAnimal
- Tiramisu no es Vegano: Mascarpone (Tiramisu -> CremaMascarpone) es IngAnimal
- Tiramisu no es Vegano: HuevoGallina (Tiramisu -> CremaMascarpone) es IngAnimal
- HeladoDePistacho no es SinLactosa: Leche (HeladoDePistacho -> BaseHelado) es ConLactosa
- HeladoDePistacho no es SinLactosa: Nata (HeladoDePistacho -> BaseHelado) es ConLactosa
- HeladoDePistacho no es Vegano: Leche (HeladoDePistacho -> BaseHelado) es IngAnimal
- HeladoDePistacho no es Vegano: Nata (HeladoDePistacho -> BaseHelado) es IngAnimal
