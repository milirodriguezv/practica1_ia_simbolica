"""Los mapas (grafos) que colorea el agente.

Solo datos, nada de logica.

Cada mapa es un diccionario con:
    regiones:    lista de nombres
    adyacencias: lista de pares (a, b) de regiones que comparten frontera
    posiciones:  region -> (x, y), solo para dibujar

    AUSTRALIA  7 regiones, 9 fronteras (libro 4a ed. figura 6.1).
               Necesita 3 colores.
    EEUU       48 estados contiguos, 105 fronteras. Necesita 4 colores:
               Nevada esta rodeado por un ciclo de 5 estados
               (OR-ID-UT-AZ-CA), y un ciclo impar ya pide 3 colores.
               Los estados que solo se tocan en un punto (Four Corners:
               AZ-CO y NM-UT) no se consideran vecinos.
"""


def aristas(vecinos):
    """Convierte un diccionario de vecinos en una lista de fronteras.

    Args:
        vecinos: Diccionario region -> lista de regiones vecinas.

    Returns:
        Lista ordenada de pares (a, b) con a < b, sin repetidos.
    """
    return sorted({tuple(sorted((a, b))) for a, lista in vecinos.items() for b in lista})


AUSTRALIA = {
    "regiones": ["WA", "NT", "SA", "Q", "NSW", "V", "T"],
    "adyacencias": [
        ("WA", "NT"), ("WA", "SA"), ("NT", "SA"), ("NT", "Q"), ("SA", "Q"),
        ("SA", "NSW"), ("SA", "V"), ("Q", "NSW"), ("NSW", "V"),
        # T (Tasmania) no tiene vecinos, es una isla
    ],
    # posiciones aproximadas, para que el dibujo se parezca al mapa
    "posiciones": {
        "WA": (0.0, 1.5), "NT": (1.3, 2.7), "SA": (1.6, 1.2), "Q": (2.8, 2.7),
        "NSW": (2.9, 1.2), "V": (2.7, 0.2), "T": (3.0, -1.0),
    },
}

VECINOS_EEUU = {
    "AL": ["FL", "GA", "MS", "TN"],
    "AZ": ["CA", "NM", "NV", "UT"],
    "AR": ["LA", "MO", "MS", "OK", "TN", "TX"],
    "CA": ["AZ", "NV", "OR"],
    "CO": ["KS", "NE", "NM", "OK", "UT", "WY"],
    "CT": ["MA", "NY", "RI"],
    "DE": ["MD", "NJ", "PA"],
    "FL": ["AL", "GA"],
    "GA": ["AL", "FL", "NC", "SC", "TN"],
    "ID": ["MT", "NV", "OR", "UT", "WA", "WY"],
    "IL": ["IA", "IN", "KY", "MO", "WI"],
    "IN": ["IL", "KY", "MI", "OH"],
    "IA": ["IL", "MN", "MO", "NE", "SD", "WI"],
    "KS": ["CO", "MO", "NE", "OK"],
    "KY": ["IL", "IN", "MO", "OH", "TN", "VA", "WV"],
    "LA": ["AR", "MS", "TX"],
    "ME": ["NH"],
    "MD": ["DE", "PA", "VA", "WV"],
    "MA": ["CT", "NH", "NY", "RI", "VT"],
    "MI": ["IN", "OH", "WI"],
    "MN": ["IA", "ND", "SD", "WI"],
    "MS": ["AL", "AR", "LA", "TN"],
    "MO": ["AR", "IA", "IL", "KS", "KY", "NE", "OK", "TN"],
    "MT": ["ID", "ND", "SD", "WY"],
    "NE": ["CO", "IA", "KS", "MO", "SD", "WY"],
    "NV": ["AZ", "CA", "ID", "OR", "UT"],
    "NH": ["MA", "ME", "VT"],
    "NJ": ["DE", "NY", "PA"],
    "NM": ["AZ", "CO", "OK", "TX"],
    "NY": ["CT", "MA", "NJ", "PA", "VT"],
    "NC": ["GA", "SC", "TN", "VA"],
    "ND": ["MN", "MT", "SD"],
    "OH": ["IN", "KY", "MI", "PA", "WV"],
    "OK": ["AR", "CO", "KS", "MO", "NM", "TX"],
    "OR": ["CA", "ID", "NV", "WA"],
    "PA": ["DE", "MD", "NJ", "NY", "OH", "WV"],
    "RI": ["CT", "MA"],
    "SC": ["GA", "NC"],
    "SD": ["IA", "MN", "MT", "ND", "NE", "WY"],
    "TN": ["AL", "AR", "GA", "KY", "MO", "MS", "NC", "VA"],
    "TX": ["AR", "LA", "NM", "OK"],
    "UT": ["AZ", "CO", "ID", "NV", "WY"],
    "VT": ["MA", "NH", "NY"],
    "VA": ["KY", "MD", "NC", "TN", "WV"],
    "WA": ["ID", "OR"],
    "WV": ["KY", "MD", "OH", "PA", "VA"],
    "WI": ["IA", "IL", "MI", "MN"],
    "WY": ["CO", "ID", "MT", "NE", "SD", "UT"],
}

EEUU = {
    "regiones": sorted(VECINOS_EEUU),
    "adyacencias": aristas(VECINOS_EEUU),
    # centro aproximado de cada estado (longitud, latitud), para dibujar
    "posiciones": {
        "AL": (-86.8, 32.8), "AZ": (-111.7, 34.3), "AR": (-92.4, 34.9), "CA": (-119.5, 37.2),
        "CO": (-105.5, 39.0), "CT": (-72.7, 41.6), "DE": (-75.5, 39.0), "FL": (-81.7, 28.6),
        "GA": (-83.4, 32.7), "ID": (-114.6, 44.4), "IL": (-89.2, 40.0), "IN": (-86.3, 39.9),
        "IA": (-93.5, 42.1), "KS": (-98.4, 38.5), "KY": (-85.3, 37.5), "LA": (-92.0, 31.1),
        "ME": (-69.2, 45.4), "MD": (-76.8, 39.0), "MA": (-71.8, 42.3), "MI": (-84.7, 43.7),
        "MN": (-94.3, 46.3), "MS": (-89.7, 32.7), "MO": (-92.5, 38.4), "MT": (-109.6, 47.0),
        "NE": (-99.8, 41.5), "NV": (-116.6, 39.3), "NH": (-71.6, 43.7), "NJ": (-74.7, 40.2),
        "NM": (-106.1, 34.4), "NY": (-75.5, 42.9), "NC": (-79.4, 35.6), "ND": (-100.5, 47.5),
        "OH": (-82.8, 40.3), "OK": (-97.5, 35.6), "OR": (-120.5, 43.9), "PA": (-77.8, 40.9),
        "RI": (-71.5, 41.7), "SC": (-80.9, 33.9), "SD": (-100.2, 44.4), "TN": (-86.3, 35.9),
        "TX": (-99.3, 31.5), "UT": (-111.7, 39.3), "VT": (-72.7, 44.1), "VA": (-78.8, 37.5),
        "WA": (-120.4, 47.4), "WV": (-80.6, 38.6), "WI": (-89.8, 44.6), "WY": (-107.5, 43.0),
    },
}
