"""Dibujo de un mapa con el coloreado que encontro el agente.

Dibuja un mapa (mapas.py) con el coloreado que encontro el
LogicalAgent. No tiene nada que ver con la logica de SAT/DPLL -- es
solo la parte grafica, totalmente separada (mismo principio de
"cada cosa en su archivo" que venimos usando en todo el ejercicio).

Cada region es un circulo en su posicion aproximada y cada frontera,
una linea gris entre dos circulos.
"""

import matplotlib
matplotlib.use("Agg")  # para poder generar la imagen sin pantalla
import matplotlib.pyplot as plt


COLOR_HEX = {
    "Rojo":  "#e74c3c",
    "Verde": "#2ecc71",
    "Azul":  "#3498db",
    "Amarillo": "#f1c40f",
}


def dibujar_solucion(coloreado, mapa, titulo, nombre_archivo, tamano=2200, margen=1.0):
    """Dibuja el mapa como un grafo coloreado y lo guarda en un archivo.

    Args:
        coloreado: Diccionario region -> nombre de color (p. ej.
            {"WA": "Rojo"}). Puede ser None si el problema fue UNSAT; las
            regiones sin color se pintan en gris.
        mapa: Diccionario de mapas.py (regiones, adyacencias, posiciones).
        titulo: Titulo de la figura.
        nombre_archivo: Ruta del archivo de salida.
        tamano: Area de cada circulo, en puntos al cuadrado.
        margen: Hueco alrededor del mapa, en las unidades de las posiciones.
    """
    posiciones = mapa["posiciones"]
    figura, ejes = plt.subplots(figsize=(6, 6) if tamano >= 1000 else (10, 6))

    for region_a, region_b in mapa["adyacencias"]:
        x1, y1 = posiciones[region_a]
        x2, y2 = posiciones[region_b]
        ejes.plot([x1, x2], [y1, y2], color="gray", linewidth=1.5, zorder=1)

    for region, (x, y) in posiciones.items():
        if coloreado is None:
            color_hex = "#dddddd"
        else:
            nombre_color = coloreado.get(region)
            color_hex = COLOR_HEX.get(nombre_color, "#dddddd")

        ejes.scatter([x], [y], s=tamano, color=color_hex,
                     edgecolors="black", linewidths=1.5, zorder=2)
        ejes.text(x, y, region, ha="center", va="center",
                  fontsize=12 if tamano >= 1000 else 7, fontweight="bold", zorder=3)

    xs = [x for x, _ in posiciones.values()]
    ys = [y for _, y in posiciones.values()]
    ejes.set_xlim(min(xs) - margen, max(xs) + margen)
    ejes.set_ylim(min(ys) - margen, max(ys) + margen)
    ejes.set_title(titulo, fontsize=14)
    ejes.axis("off")

    plt.tight_layout()
    plt.savefig(nombre_archivo, dpi=150)
    plt.close(figura)
