# Consistencia de conceptos

| Concepto | ¿Satisfacible? | Testigo / motivo |
|---|---|---|
| Vegetariano ⊓ ∃contiene.Pescado | No | todo ingrediente de Pescado esta prohibido por Vegetariano |
| SinCarne ⊓ ∃contiene.Pescado | Si | plato {Anchoa} |
| SinLactosa ⊓ ∃contiene.Lacteo | Si | plato {Parmesano} |
| SinLactosa ⊓ ∃contiene.Mozzarella | No | todo ingrediente de Mozzarella esta prohibido por SinLactosa |
| SinGluten ⊓ ∃contiene.Cereal | Si | plato {Arroz} |
| SinGluten ⊓ Vegetariano ⊓ SinLactosa ⊓ ∃contiene.Lacteo | Si | plato {Parmesano} |
| Vegano ⊓ ∃contiene.Lacteo | No | todo ingrediente de Lacteo esta prohibido por Vegano |
| Vegano ⊓ SinGluten ⊓ ∃contiene.Cereal | Si | plato {Arroz} |
