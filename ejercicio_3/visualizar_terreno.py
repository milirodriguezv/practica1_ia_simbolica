"""
visualizar_terreno.py
---------------------
Dibuja el terreno del rover: mapa de calor de alturas, paredes de
crater demasiado empinadas, rocas, S, G y (cuando existan) las rutas de
cada algoritmo. Como visualizar_mapa.py del ejercicio 1, aqui no hay
nada de busqueda: es solo la parte grafica.

Las figuras se guardan en ejercicio_3/figures/.
"""

from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")  # para poder generar la imagen sin pantalla
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

CARPETA_FIGURAS = Path(__file__).parent / "figures"

COLORES_RUTAS = ["#29b6f6", "#ab47bc", "#66bb6a", "#ffa726", "#ef5350"]


def dibujar_terreno(terreno, titulo, nombre_archivo, rutas=None):
    """
    terreno: objeto Terreno (terrain.py)
    rutas:   opcional, diccionario nombre -> lista de celdas (i, j),
             p.ej. {"A* (h2)": [...], "Voraz": [...]}
    """
    rutas = rutas or {}
    figura, ejes = plt.subplots(figsize=(7, 7))

    fondo = ejes.imshow(terreno.alturas, cmap="copper", origin="upper")
    figura.colorbar(fondo, ax=ejes, fraction=0.046, pad=0.04, label="altura (m)")

    pared = np.ma.masked_where(~terreno.mascara_pendiente_excesiva(), np.ones_like(terreno.alturas))
    ejes.imshow(pared, cmap=ListedColormap(["#e53935"]), alpha=0.45, origin="upper")
    rocas = np.ma.masked_where(~terreno.rocas, np.ones_like(terreno.alturas))
    ejes.imshow(rocas, cmap=ListedColormap(["black"]), origin="upper")

    leyenda = [Patch(color="#e53935", alpha=0.45, label="Pendiente > θ_max"),
               Patch(color="black", label="Roca")]

    for color, (nombre, ruta) in zip(COLORES_RUTAS, rutas.items()):
        filas, columnas = zip(*ruta)
        ejes.plot(columnas, filas, color=color, linewidth=2)
        leyenda.append(Line2D([], [], color=color, linewidth=2, label=nombre))

    if terreno.inicio is not None:
        ejes.plot(terreno.inicio[1], terreno.inicio[0], "o", markersize=12,
                  markerfacecolor="white", markeredgecolor="black")
        leyenda.append(Line2D([], [], marker="o", linestyle="", markerfacecolor="white",
                              markeredgecolor="black", label="S (inicio)"))
    if terreno.objetivo is not None:
        ejes.plot(terreno.objetivo[1], terreno.objetivo[0], "*", markersize=18,
                  markerfacecolor="gold", markeredgecolor="black")
        leyenda.append(Line2D([], [], marker="*", linestyle="", markersize=12, markerfacecolor="gold",
                              markeredgecolor="black", label="G (objetivo)"))

    ejes.set_title(titulo, fontsize=13)
    ejes.set_xlabel("columna j")
    ejes.set_ylabel("fila i")
    ejes.legend(handles=leyenda, loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=3, fontsize=9)

    CARPETA_FIGURAS.mkdir(exist_ok=True)
    ruta_salida = CARPETA_FIGURAS / nombre_archivo
    figura.savefig(ruta_salida, dpi=150, bbox_inches="tight")
    plt.close(figura)
    print(f"Imagen guardada en {ruta_salida}")
