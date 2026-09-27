# E0. Validacion de la ontologia

Ontologia valida: 64 clases, 50 ingredientes atomicos, 10 elaborados, 8 platos, 4 categorias.

Definiciones de las categorias (TBox):

- PlatoValido ≡ Plato ⊓ ∃contiene.Ingrediente
- SinGluten ≡ PlatoValido ⊓ ∀contiene.¬ConGluten
- Vegetariano ≡ PlatoValido ⊓ ∀contiene.¬(Carne ⊔ Pescado)
- SinCarne ≡ PlatoValido ⊓ ∀contiene.¬Carne
- SinLactosa ≡ PlatoValido ⊓ ∀contiene.¬ConLactosa
