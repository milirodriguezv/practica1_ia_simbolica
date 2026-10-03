"""
ABox de la ontologia: la carta del restaurante italiano.

Aqui solo hay hechos concretos: que lleva cada ingrediente elaborado y
que lleva cada plato. Las categorias dieteticas de cada plato no se
escriben aqui: las calcula el razonador.

"etiquetas_carta" es lo que el restaurante afirma en su carta impresa.
Solo se usa para auditar la carta (experimento de auditoria), nunca para clasificar.

Supuesto de mundo cerrado: la lista de componentes de cada plato es
completa (si no aparece, el plato no lo lleva).
"""

# Ingredientes elaborados: nombre -> lista de componentes.
# Un componente puede ser un ingrediente atomico o a su vez otro
# ingrediente elaborado (relacion "contiene" transitiva).
COMPUESTOS = {
    "SalsaTonnata": ["Atun", "Anchoa", "Alcaparra", "Mayonesa", "Limon"],
    "Mayonesa": ["HuevoGallina", "AceiteOliva", "Limon", "Sal"],
    "TomatesConfitados": ["Tomate", "AceiteOliva", "Ajo", "Tomillo"],
    "MasaPizza": ["HarinaTrigo", "Agua", "Levadura", "AceiteOliva", "Sal"],
    "SalsaTomate": ["Tomate", "Ajo", "AceiteOliva", "Albahaca", "Sal"],
    "Vinagreta": ["AceiteOliva", "VinagreBalsamico", "Sal"],
    "VerdurasAsadas": ["Calabacin", "Pimiento", "Cebolla", "AceiteOliva", "Sal"],
    "Bizcochos": ["HarinaTrigo", "HuevoGallina", "Azucar"], 
    "CremaMascarpone": ["Mascarpone", "HuevoGallina", "Azucar"],
    "BaseHelado": ["Leche", "Nata", "Azucar"],
}

PLATOS = {
    # Entrantes 
    "VitelTone": {
        "tipo": "Entrante",
        "componentes": ["Ternera", "SalsaTonnata", "Alcaparra"],
        "etiquetas_carta": ["SinGluten"],
    },
    "BurrataConTomatesConfitados": {
        "tipo": "Entrante",
        "componentes": ["Burrata", "TomatesConfitados", "Albahaca"],
        "etiquetas_carta": ["SinGluten", "Vegetariano"],
    },
    # Principales 
    "PizzaMozzarella": {
        "tipo": "Principal",
        "componentes": ["MasaPizza", "SalsaTomate", "Mozzarella", "Albahaca"],
        "etiquetas_carta": ["Vegetariano"],
    },
    "EspaguetisAlPomodoro": {
        "tipo": "Principal",
        "componentes": ["Espaguetis", "SalsaTomate", "Albahaca"],
        # La carta solo dice "Vegetariano": la auditoria debe avisar
        # de que tambien es Vegano, pero no de SinCarne ni SinLactosa,
        # que ya van implicadas por Vegano.
        "etiquetas_carta": ["Vegetariano"],
    },
    "PastaCarbonara": {
        "tipo": "Principal",
        "componentes": ["Espaguetis", "Guanciale", "HuevoGallina",
                        "PecorinoRomano", "Pimienta"],
        "etiquetas_carta": [],
    },
    "EnsaladaRuculaPeraParmesano": {
        "tipo": "Principal",
        "componentes": ["Rucula", "Pera", "Parmesano", "Nuez", "Vinagreta"],
        "etiquetas_carta": ["SinGluten", "Vegetariano"],
    },
    "SalmonConVerdurasAlHorno": {
        "tipo": "Principal",
        "componentes": ["Salmon", "VerdurasAsadas", "Limon"],
        "etiquetas_carta": ["SinGluten", "SinLactosa"],
    },
    # Postres 
    "Tiramisu": {
        "tipo": "Postre",
        "componentes": ["Bizcochos", "CremaMascarpone", "Cafe", "Cacao"],
        "etiquetas_carta": ["Vegetariano"],
    },
    "HeladoDePistacho": {
        "tipo": "Postre",
        "componentes": ["BaseHelado", "Pistacho"],
        # ERROR INTRODUCIDO A PROPOSITO para el experimento de auditoria:
        # la carta afirma "SinLactosa", pero la lactosa esta escondida
        # dentro del elaborado BaseHelado (leche y nata).
        "etiquetas_carta": ["SinGluten", "Vegetariano", "SinLactosa"],
    },
}

CARTA = {
    "compuestos": COMPUESTOS,
    "platos": PLATOS,
}
