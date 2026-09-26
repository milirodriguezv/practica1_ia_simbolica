"""
visualizar_mapa.py
-------------------
Dibuja el mapa de Australia con el coloreado que encontro el
LogicalAgent. No tiene nada que ver con la logica de SAT/DPLL -- es
solo la parte grafica, totalmente separada (mismo principio de
"cada cosa en su archivo" que venimos usando en todo el ejercicio).

Las posiciones de las regiones son aproximadas, solo para que el
dibujo se parezca a la disposicion real del mapa de Australia.
"""

import matplotlib
matplotlib.use("Agg")  # para poder generar la imagen sin pantalla
import matplotlib.pyplot as plt


POSICIONES = {
    "WA":  (0.0, 1.5),
    "NT":  (1.3, 2.7),
    "SA":  (1.6, 1.2),
    "Q":   (2.8, 2.7),
    "NSW": (2.9, 1.2),
    "V":   (2.7, 0.2),
    "T":   (3.0, -1.0),
}

COLOR_HEX = {
    "Rojo":  "#e74c3c",
    "Verde": "#2ecc71",
    "Azul":  "#3498db",
}


def dibujar_solucion(coloreado, adyacencias, titulo, nombre_archivo):
    """
    coloreado: diccionario region -> nombre de color (ej: {"WA": "Rojo", ...})
               puede ser None si el problema fue UNSAT
    adyacencias: lista de tuplas (region_a, region_b)
    """
    figura, ejes = plt.subplots(figsize=(6, 6))

    for region_a, region_b in adyacencias:
        x1, y1 = POSICIONES[region_a]
        x2, y2 = POSICIONES[region_b]
        ejes.plot([x1, x2], [y1, y2], color="gray", linewidth=1.5, zorder=1)

    for region, (x, y) in POSICIONES.items():
        if coloreado is None:
            color_hex = "#dddddd"
        else:
            nombre_color = coloreado.get(region)
            color_hex = COLOR_HEX.get(nombre_color, "#dddddd")

        ejes.scatter([x], [y], s=2200, color=color_hex,
                     edgecolors="black", linewidths=1.5, zorder=2)
        ejes.text(x, y, region, ha="center", va="center",
                  fontsize=12, fontweight="bold", zorder=3)

    ejes.set_title(titulo, fontsize=14)
    ejes.axis("off")
    ejes.set_xlim(-1, 4)
    ejes.set_ylim(-2, 3.5)

    plt.tight_layout()
    plt.savefig(nombre_archivo, dpi=150)
    plt.close(figura)
