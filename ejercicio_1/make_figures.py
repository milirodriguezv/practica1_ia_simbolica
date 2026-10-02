"""
make_figures.py
---------------
Lee results/*.csv (de run_experiments.py) y genera las figuras de la
memoria en figures/ (.pdf para LaTeX y .png para verlas rapido):

    e2_ablacion      decisiones de DPLL frente a n, con y sin cada regla
    e3_transicion    P(SAT) y decisiones de DPLL frente a m/n

Al final imprime los numeros clave para el texto.
"""

from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

CARPETA = Path(__file__).parent
RESULTADOS = CARPETA / "results"
FIGURAS = CARPETA / "figures"
RAZON_CRITICA = 4.26

# Paleta validada para daltonismo (la misma del ejercicio 3)
COLORES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
TINTA, GRIS = "#0b0b0b", "#8a8984"

plt.rcParams.update({
    "font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": GRIS, "axes.grid": True, "grid.color": "#e4e3df",
    "axes.axisbelow": True, "lines.linewidth": 2, "legend.frameon": False,
})


def guardar(figura, nombre):
    FIGURAS.mkdir(exist_ok=True)
    for extension in ("pdf", "png"):
        figura.savefig(FIGURAS / f"{nombre}.{extension}", dpi=150, bbox_inches="tight")
    plt.close(figura)
    print(f"  figures/{nombre}.pdf")


ETIQUETAS = {"backtracking basico": "backtracking básico",
             "sin clausula unitaria": "sin cláusula unitaria",
             "sin simbolo puro": "sin símbolo puro", "DPLL completo": "DPLL completo"}


def fig_ablacion(e2):
    """Mediana de decisiones frente a n (escala log): sin clausula unitaria
    el crecimiento es exponencial."""
    mediana = e2.groupby(["configuracion", "n"]).decisiones.median()
    orden = ["backtracking basico", "sin clausula unitaria", "sin simbolo puro", "DPLL completo"]
    figura, ejes = plt.subplots(figsize=(5.5, 3.6))
    for color, configuracion in zip(COLORES, orden):
        serie = mediana.loc[configuracion]
        estilo = "--" if configuracion == "sin simbolo puro" else "-"
        ejes.plot(serie.index, serie.values + 1, estilo, color=color, marker="o",
                  markersize=4, label=ETIQUETAS[configuracion])
    ejes.set_yscale("log")
    ejes.set_xlabel("n (variables)")
    ejes.set_ylabel("decisiones + 1 (mediana, log)")
    ejes.set_title(f"Ablación de DPLL en 3-SAT aleatorio (m/n = {RAZON_CRITICA})",
                   fontsize=11, loc="left")
    ejes.legend(fontsize=9)
    guardar(figura, "e2_ablacion")


def fig_transicion(e3):
    """Izquierda: probabilidad de SAT. Derecha: mediana de decisiones."""
    figura, (izq, der) = plt.subplots(1, 2, figsize=(10, 3.6))
    for color, (n, datos) in zip(COLORES, e3.groupby("n")):
        por_razon = datos.groupby("razon")
        izq.plot(por_razon.sat.mean(), color=color, marker="o", markersize=3, label=f"n = {n}")
        der.plot(por_razon.decisiones.median() + 1, color=color, marker="o", markersize=3,
                 label=f"n = {n}")
    for ejes in (izq, der):
        ejes.axvline(RAZON_CRITICA, color=GRIS, linewidth=1, linestyle=":")
        ejes.set_xlabel("m/n (cláusulas por variable)")
    izq.annotate(f"m/n = {RAZON_CRITICA}", (RAZON_CRITICA, 0.95), xytext=(5, 0),
                 textcoords="offset points", fontsize=9, color=TINTA)
    izq.set_ylabel("proporción de fórmulas SAT")
    izq.set_title("Probabilidad de SAT", fontsize=11, loc="left")
    der.set_yscale("log")
    der.set_ylabel("decisiones + 1 (mediana, log)")
    der.set_title("Coste de DPLL", fontsize=11, loc="left")
    izq.legend(fontsize=9)
    figura.suptitle("Transición de fase en 3-SAT aleatorio (30 fórmulas por punto)",
                    fontsize=11, x=0.01, ha="left")
    figura.tight_layout()
    guardar(figura, "e3_transicion")


def resumen(e1, e2, e3):
    print("\nResumen:")
    print(f"  E1: DPLL = fuerza bruta en {e1.coinciden.sum()}/{len(e1)} formulas "
          f"({e1.sat_fuerza_bruta.sum()} SAT)")
    m = e2.groupby(["configuracion", "n"]).decisiones.median().unstack()
    n_max = m.columns.max()
    for configuracion in m.index:
        print(f"  E2 n={n_max}: {configuracion}: {m.loc[configuracion, n_max]:.0f} decisiones (mediana)")
    for n, datos in e3.groupby("n"):
        p = datos.groupby("razon").sat.mean()
        pico = datos.groupby("razon").decisiones.median().idxmax()
        cruce = p[p <= 0.5].index.min()
        print(f"  E3 n={n}: P(SAT) <= 0.5 desde m/n = {cruce}, maximo de decisiones en m/n = {pico}")


if __name__ == "__main__":
    e1, e2, e3 = (pd.read_csv(RESULTADOS / f) for f in
                  ["e1_correccion.csv", "e2_ablacion.csv", "e3_transicion.csv"])
    print("Figuras:")
    fig_ablacion(e2)
    fig_transicion(e3)
    resumen(e1, e2, e3)
