"""
TBox de la ontologia del restaurante italiano.

Aqui solo hay conocimiento general: que es cada ingrediente y como se
definen las categorias dieteticas. No aparece ningun plato concreto
(los platos estan en carta.py).

Notacion de logica descriptiva usada en la memoria:
    A ⊑ B       "todo A es un B" (subclase)
    ∀contiene.¬X  "todo lo que el plato contiene es no-X", que es lo mismo que "el plato no contiene nada que sea X"
"""


# 1. Taxonomia de ingredientes
# Cada clase apunta a la lista de sus padres directos.
# Una clase puede tener varios padres (herencia multiple): por ejemplo,
# la Mozzarella es un Lacteo y ademas es ConLactosa.
# Las clases que no son padre de nadie son las "hojas": los ingredientes atomicos reales que se usan en la carta.

TAXONOMIA = {
    # Raiz
    "Ingrediente": [],

    # Nivel 1: particion animal / no animal
    "IngAnimal": ["Ingrediente"],
    "IngNoAnimal": ["Ingrediente"],

    # Subclases de IngAnimal
    "Carne": ["IngAnimal"],
    "Pescado": ["IngAnimal"],
    "Lacteo": ["IngAnimal"],
    "Huevo": ["IngAnimal"],

    # Subclases de IngNoAnimal
    "Verdura": ["IngNoAnimal"],
    "Fruta": ["IngNoAnimal"],
    "FrutoSeco": ["IngNoAnimal"],
    "Cereal": ["IngNoAnimal"],
    "Despensa": ["IngNoAnimal"],  # aceite, sal, azucar, cafe...

    # Clases transversales: no siguen la jerarquia animal / no animal
    "ConGluten": ["Ingrediente"],
    "ConLactosa": ["Ingrediente"],

    # Hojas (ingredientes atomicos) 
    # Carne
    "Ternera": ["Carne"],
    "Guanciale": ["Carne"],
    "Pollo": ["Carne"],
    "Cerdo": ["Carne"],
    "Pavo": ["Carne"],
    "Cordero": ["Carne"],
    "Jamon": ["Carne"],
    # Pescado
    "Atun": ["Pescado"],
    "Anchoa": ["Pescado"],
    "Salmon": ["Pescado"],
    "Merluza": ["Pescado"],
    # Lacteos
    "Leche": ["Lacteo", "ConLactosa"],
    "Nata": ["Lacteo", "ConLactosa"],
    "Mozzarella": ["Lacteo", "ConLactosa"],
    "Burrata": ["Lacteo", "ConLactosa"],
    "Mascarpone": ["Lacteo", "ConLactosa"],
    "PecorinoRomano": ["Lacteo", "ConLactosa"],
    "Parmesano": ["Lacteo"],
    # Huevo
    "HuevoGallina": ["Huevo"],
    # Verduras y hierbas
    "Tomate": ["Verdura"],
    "Rucula": ["Verdura"],
    "Calabacin": ["Verdura"],
    "Pimiento": ["Verdura"],
    "Cebolla": ["Verdura"],
    "Ajo": ["Verdura"],
    "Alcaparra": ["Verdura"],
    "Albahaca": ["Verdura"],
    "Tomillo": ["Verdura"],
    # Fruta y frutos secos
    "Pera": ["Fruta"],
    "Mandarina": ["Fruta"],
    "Naranja": ["Fruta"],
    "Manzana": ["Fruta"],
    "Platano": ["Fruta"],
    "Limon": ["Fruta"],
    "Pistacho": ["FrutoSeco"],
    "Nuez": ["FrutoSeco"],
    # Cereales: los de trigo llevan gluten, el arroz no.
    # (El arroz no se usa en la carta, pero forma parte del conocimiento
    # general del dominio: la TBox no depende de los platos concretos.)
    "HarinaTrigo": ["Cereal", "ConGluten"],
    "Espaguetis": ["Cereal", "ConGluten"],
    "Arroz": ["Cereal"],
    "Quinoa": ["Cereal"],
    "Maiz": ["Cereal"],
    # Despensa
    "AceiteOliva": ["Despensa"],
    "Sal": ["Despensa"],
    "Pimienta": ["Despensa"],
    "Azucar": ["Despensa"],
    "VinagreBalsamico": ["Despensa"],
    "Levadura": ["Despensa"],
    "Agua": ["Despensa"],
    "Cafe": ["Despensa"],
    "Cacao": ["Despensa"],
}


# 2. Axiomas sobre la taxonomia
# Grupos de clases disjuntas: ningun ingrediente puede estar en dos
# clases del mismo grupo (IngAnimal ⊓ IngNoAnimal ⊑ ⊥).
DISJUNTAS = [
    ["IngAnimal", "IngNoAnimal"],
]

# Descomposiciones exhaustivas: los hijos cubren todo al padre: cualquier cosa 
# que sea del padre cae en al menos una de las cajas hijas.
# (disjunta + exhaustiva = particion)
EXHAUSTIVAS = {
    "Ingrediente": ["IngAnimal", "IngNoAnimal"],
    "IngAnimal": ["Carne", "Pescado", "Lacteo", "Huevo"],
}

# Tipos de plato (particion de Plato)
TIPOS_PLATO = ["Entrante", "Principal", "Postre"]


# 3. Categorias dieteticas (DEFINIDAS, no etiquetadas a mano)
# Todas tienen la misma forma:
#     C ≡ PlatoValido ⊓ ∀contiene.¬(X1 ⊔ ... ⊔ Xn)
# donde PlatoValido ≡ Plato ⊓ ∃contiene.Ingrediente.
# Por eso basta con guardar la lista de clases prohibidas F(C).
CATEGORIAS = {
    "SinGluten": {
        "prohibidas": ["ConGluten"],
        "formula": "PlatoValido ⊓ ∀contiene.¬ConGluten",
    },
    "Vegetariano": {
        "prohibidas": ["Carne", "Pescado"],
        "formula": "PlatoValido ⊓ ∀contiene.¬(Carne ⊔ Pescado)",
    },
    # SinCarne es mas permisiva que Vegetariano (admite pescado).
    # Es habitual en cartas (cuaresma, dietas religiosas, pescetarianos)
    # y permite comprobar una subsuncion real: Vegetariano ⊑ SinCarne.
    "SinCarne": {
        "prohibidas": ["Carne"],
        "formula": "PlatoValido ⊓ ∀contiene.¬Carne",
    },
    "SinLactosa": {
        "prohibidas": ["ConLactosa"],
        "formula": "PlatoValido ⊓ ∀contiene.¬ConLactosa",
    },
    # Vegano prohibe todo lo animal. No hace falta declarar que es mas
    # estricta que las demas: el razonador infiere Vegano ⊑ Vegetariano,
    # Vegano ⊑ SinCarne y Vegano ⊑ SinLactosa (todo ConLactosa es Lacteo,
    # y todo Lacteo es IngAnimal).
    "Vegano": {
        "prohibidas": ["IngAnimal"],
        "formula": "PlatoValido ⊓ ∀contiene.¬IngAnimal",
    },
}

# Todo junto en un diccionario para pasarlo al razonador
ONTOLOGIA = {
    "taxonomia": TAXONOMIA,
    "disjuntas": DISJUNTAS,
    "exhaustivas": EXHAUSTIVAS,
    "tipos_plato": TIPOS_PLATO,
    "categorias": CATEGORIAS,
}
