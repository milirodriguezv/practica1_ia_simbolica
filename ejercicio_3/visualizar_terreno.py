"""Dibujo del terreno del rover y de las rutas.

Dibuja el terreno del rover: mapa de calor de alturas, paredes de
crater demasiado empinadas, rocas, S, G y (cuando existan) las rutas de
cada algoritmo. Como visualizar_mapa.py del ejercicio 1, aqui no hay
nada de busqueda: es solo la parte grafica.

    dibujar_terreno            -> un mapa con todas las rutas superpuestas
    dibujar_rutas_por_separado -> un panel por algoritmo (ruta + nodos expandidos)

Las figuras se guardan en ejercicio_3/figures/.
"""

import math
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")  # para poder generar la imagen sin pantalla
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

CARPETA_FIGURAS = Path(__file__).parent / "figures"

# Colores de las rutas sobre el mapa, en el orden en que se dibujan.
# Son tonos claros para que se vean sobre el fondo cobrizo.
COLORES_RUTAS = ["#29b6f6", "#ab47bc", "#66bb6a", "#ffa726", "#ef5350"]

# Un color por algoritmo para las graficas de make_figures.py.
COLOR_ALGORITMO = {
    "UCS": "#6a4c93",         # morado
    "A* (h1)": "#f2a541",     # naranja arena
    "A* (h2)": "#c1440e",     # rojo Marte
    "Voraz (h1)": "#74b49b",  # verde claro
    "Voraz (h2)": "#2a7f62",  # verde oscuro
}
# Trazo y grosor distintos por ruta: si dos rutas coinciden, la de abajo
# (mas gruesa) sigue asomando por los huecos de la de arriba.
ESTILOS_RUTAS = [("-", 5.0), ("-", 3.0), ("--", 2.5), (":", 2.5), ("-.", 2.0)]
COLOR_EXPANDIDOS = "#1565c0"
COLOR_PARED = "#e53935"


def _dibujar_fondo(ejes, terreno):
    """Dibuja las alturas, las paredes demasiado empinadas y las rocas.

    Args:
        ejes: Ejes de matplotlib.
        terreno: Terreno a dibujar.

    Returns:
        Tupla (imagen de alturas, entradas de la leyenda). La imagen sirve
        para la barra de color.
    """
    fondo = ejes.imshow(terreno.alturas, cmap="copper", origin="upper")

    pared = np.ma.masked_where(~terreno.mascara_pendiente_excesiva(), np.ones_like(terreno.alturas))
    ejes.imshow(pared, cmap=ListedColormap([COLOR_PARED]), alpha=0.45, origin="upper")
    rocas = np.ma.masked_where(~terreno.rocas, np.ones_like(terreno.alturas))
    ejes.imshow(rocas, cmap=ListedColormap(["black"]), origin="upper")

    leyenda = [Patch(color=COLOR_PARED, alpha=0.45, label="Pendiente > θ_max"),
               Patch(color="black", label="Roca")]
    return fondo, leyenda


def _dibujar_inicio_objetivo(ejes, terreno):
    """Marca S y G en el mapa.

    Args:
        ejes: Ejes de matplotlib.
        terreno: Terreno con inicio y objetivo.

    Returns:
        Entradas de la leyenda para S y G.
    """
    leyenda = []
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
    return leyenda


def _guardar(figura, nombre_archivo):
    """Guarda la figura en figures/ y la cierra.

    Args:
        figura: Figura de matplotlib.
        nombre_archivo: Nombre del archivo de salida.
    """
    CARPETA_FIGURAS.mkdir(exist_ok=True)
    ruta_salida = CARPETA_FIGURAS / nombre_archivo
    figura.savefig(ruta_salida, dpi=150, bbox_inches="tight")
    plt.close(figura)
    print(f"Imagen guardada en {ruta_salida}")


def dibujar_terreno(terreno, titulo, nombre_archivo, rutas=None):
    """Dibuja un mapa con todas las rutas superpuestas.

    Args:
        terreno: Terreno (terrain.py).
        titulo: Titulo de la figura.
        nombre_archivo: Nombre del archivo de salida.
        rutas: Diccionario nombre -> lista de celdas (i, j), p. ej.
            {"A* (h2)": [...], "Voraz (h2)": [...]}. Opcional.
    """
    rutas = rutas or {}
    figura, ejes = plt.subplots(figsize=(7, 7))

    fondo, leyenda = _dibujar_fondo(ejes, terreno)
    figura.colorbar(fondo, ax=ejes, fraction=0.046, pad=0.04, label="altura (m)")

    for color, (estilo, grosor), (nombre, ruta) in zip(COLORES_RUTAS, ESTILOS_RUTAS, rutas.items()):
        filas, columnas = zip(*ruta)
        ejes.plot(columnas, filas, color=color, linestyle=estilo, linewidth=grosor)
        leyenda.append(Line2D([], [], color=color, linestyle=estilo, linewidth=grosor, label=nombre))

    leyenda += _dibujar_inicio_objetivo(ejes, terreno)

    ejes.set_title(titulo, fontsize=13)
    ejes.set_xlabel("columna j")
    ejes.set_ylabel("fila i")
    ejes.legend(handles=leyenda, loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=3, fontsize=9)
    _guardar(figura, nombre_archivo)


def dibujar_rutas_por_separado(terreno, titulo, nombre_archivo, rutas, expandidos=None, subtitulos=None):
    """Dibuja un panel por algoritmo, en una rejilla de 2 columnas.

    Args:
        terreno: Terreno (terrain.py).
        titulo: Titulo de la figura.
        nombre_archivo: Nombre del archivo de salida.
        rutas: Diccionario nombre -> lista de celdas (i, j).
        expandidos: Diccionario nombre -> celdas expandidas, que se
            sombrean para ver cuanto ha explorado cada algoritmo. Opcional.
        subtitulos: Diccionario nombre -> texto bajo el nombre (p. ej.
            coste y nodos). Opcional.
    """
    expandidos = expandidos or {}
    subtitulos = subtitulos or {}
    filas_rejilla = math.ceil(len(rutas) / 2)
    figura, ejes_todos = plt.subplots(filas_rejilla, 2, figsize=(11, 5.5 * filas_rejilla),
                                      squeeze=False, constrained_layout=True)

    for ejes, color, (nombre, ruta) in zip(ejes_todos.flat, COLORES_RUTAS, rutas.items()):
        fondo, leyenda = _dibujar_fondo(ejes, terreno)

        if nombre in expandidos:
            mascara = np.zeros(terreno.alturas.shape, dtype=bool)
            for celda in expandidos[nombre]:
                mascara[celda] = True
            capa = np.ma.masked_where(~mascara, np.ones_like(terreno.alturas))
            ejes.imshow(capa, cmap=ListedColormap([COLOR_EXPANDIDOS]), alpha=0.4, origin="upper")
            leyenda.append(Patch(color=COLOR_EXPANDIDOS, alpha=0.4, label="Nodos expandidos"))

        filas, columnas = zip(*ruta)
        ejes.plot(columnas, filas, color=color, linewidth=2.5)
        leyenda.append(Line2D([], [], color="dimgray", linewidth=2.5, label="Ruta (color del algoritmo)"))
        leyenda += _dibujar_inicio_objetivo(ejes, terreno)

        texto = nombre if nombre not in subtitulos else f"{nombre}\n{subtitulos[nombre]}"
        ejes.set_title(texto, fontsize=11)
        ejes.set_xticks([])
        ejes.set_yticks([])

    for ejes in list(ejes_todos.flat)[len(rutas):]:  # paneles sobrantes
        ejes.axis("off")

    figura.colorbar(fondo, ax=ejes_todos, fraction=0.03, pad=0.02, label="altura (m)")
    figura.legend(handles=leyenda, loc="outside lower center", ncol=len(leyenda), fontsize=9)
    figura.suptitle(titulo, fontsize=14)
    _guardar(figura, nombre_archivo)
