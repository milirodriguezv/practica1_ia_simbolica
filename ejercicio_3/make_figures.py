"""
make_figures.py
---------------
Lee results/*.csv (de run_experiments.py) y genera las figuras y tablas
de la memoria:

    figures/velocidad_pendiente.pdf  v(theta), figura de la metodologia
    figures/e2_nodos_vs_d.pdf        nodos expandidos frente a d (UCS, A* h1, A* h2)
    figures/e3_voraz.pdf             sobrecoste y nodos expandidos de la voraz frente a A*
    figures/e4_asimetria.pdf         diferencia ida/vuelta frente al desnivel S -> G
    figures/e5_escalabilidad.pdf     tiempo, nodos y frontera maxima frente a N
    results/tabla_b_estrella_*.tex   tabla estilo figura 3.26 (generados y b* frente a d)
    results/tabla_e1.tex             E1: error frente a networkx

Cada figura se guarda en .pdf (para LaTeX) y en .png (para verla rapido).
Las rutas sobre el mapa las dibuja main.py.

Colores: un color fijo por algoritmo en todas las figuras (paleta de
referencia validada para daltonismo); el tipo de terreno va en paneles
separados, no en color.
"""

import math
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from parametros import K_BAJ, K_SUB, THETA_MAX, V_MAX
from problem import velocidad

CARPETA = Path(__file__).parent
RESULTADOS = CARPETA / "results"
FIGURAS = CARPETA / "figures"

COLOR = {  # el color sigue al algoritmo, en todas las figuras
    "UCS": "#2a78d6",
    "A* (h1)": "#eb6834",
    "A* (h2)": "#1baf7a",
    "Voraz (h2)": "#eda100",
}
NEUTRO = "#52514e"
TINTA = "#0b0b0b"
TERRENOS = {"base": "Terreno base", "abrupto": "Terreno abrupto"}

plt.rcParams.update({
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "#8a8984",
    "axes.labelcolor": TINTA,
    "xtick.color": NEUTRO,
    "ytick.color": NEUTRO,
    "axes.grid": True,
    "grid.color": "#e4e3df",
    "grid.linewidth": 0.8,
    "axes.axisbelow": True,
    "lines.linewidth": 2,
    "legend.frameon": False,
})


def guardar(figura, nombre):
    FIGURAS.mkdir(exist_ok=True)
    for extension in ("pdf", "png"):
        figura.savefig(FIGURAS / f"{nombre}.{extension}", dpi=150, bbox_inches="tight")
    plt.close(figura)
    print(f"  figures/{nombre}.pdf")


# A*(h1) y A*(h2) acaban muy cerca: una etiqueta un poco arriba y otra abajo
DESPLAZAMIENTO = {"A* (h1)": 4, "A* (h2)": -4}


def etiqueta_final(ejes, x, y, texto, color):
    """Etiqueta directa al final de una linea (texto en tinta, marca en color)."""
    ejes.plot(x, y, "o", color=color, markersize=5)
    ejes.annotate(texto, (x, y), xytext=(6, DESPLAZAMIENTO.get(texto, 0)), textcoords="offset points",
                  va="center", fontsize=9, color=TINTA)


# ---------------------------------------------------------------------


def fig_velocidad():
    """v(theta) / V_MAX: subir frena mas que bajar."""
    grados = np.linspace(-math.degrees(THETA_MAX), math.degrees(THETA_MAX), 201)
    v = [velocidad(math.radians(g)) / V_MAX for g in grados]

    figura, ejes = plt.subplots(figsize=(5.5, 3.2))
    ejes.plot(grados, v, color=COLOR["UCS"])
    ejes.axvline(0, color="#8a8984", linewidth=0.8)
    limite = math.degrees(THETA_MAX)
    for g, texto in [(-limite, f"bajada: {1 - K_BAJ:.1f}·v_max"), (limite, f"subida: {1 - K_SUB:.1f}·v_max")]:
        valor = velocidad(math.radians(g)) / V_MAX
        ejes.plot(g, valor, "o", color=COLOR["UCS"], markersize=6)
        ejes.annotate(texto, (g, valor), xytext=(0, -14), textcoords="offset points",
                      ha="left" if g < 0 else "right", fontsize=9)
    ejes.set_xlabel("pendiente θ (grados; > 0 sube)")
    ejes.set_ylabel("v(θ) / v_max")
    ejes.set_ylim(0, 1.08)
    ejes.set_title("Velocidad del rover según la pendiente", fontsize=11, loc="left")
    guardar(figura, "velocidad_pendiente")


MIN_CASOS = 5  # intervalos de d con menos casos no se muestran (poco fiables)


def agrupar_por_d(df, ancho=20):
    """Intervalos de d de 'ancho' pasos: [1, 20], [21, 40]..."""
    df = df.copy()
    df["d_grupo"] = ((df["d"] - 1) // ancho) * ancho + ancho / 2 + 0.5
    return df


def fig_e2(e2):
    """Nodos expandidos frente a d: mediana y rango intercuartilico."""
    e2 = agrupar_por_d(e2)
    casos = e2[e2.algoritmo == "UCS"].groupby(["terreno", "d_grupo"]).size()
    validos = casos[casos >= MIN_CASOS].index
    e2 = e2[e2.set_index(["terreno", "d_grupo"]).index.isin(validos)]
    figura, ejes_todos = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
    for ejes, (tipo, titulo) in zip(ejes_todos, TERRENOS.items()):
        datos = e2[e2.terreno == tipo]
        for algoritmo in ["UCS", "A* (h1)", "A* (h2)"]:
            g = datos[datos.algoritmo == algoritmo].groupby("d_grupo")["expandidos"]
            mediana, q1, q3 = g.median(), g.quantile(0.25), g.quantile(0.75)
            ejes.fill_between(mediana.index, q1, q3, color=COLOR[algoritmo], alpha=0.15, linewidth=0)
            ejes.plot(mediana.index, mediana, color=COLOR[algoritmo], label=algoritmo)
            etiqueta_final(ejes, mediana.index[-1], mediana.iloc[-1], algoritmo, COLOR[algoritmo])
        ejes.set_yscale("log")
        ejes.set_xlabel("profundidad de la solución d (pasos)")
        ejes.set_title(titulo, fontsize=11, loc="left")
        ejes.set_xlim(right=ejes.get_xlim()[1] * 1.15)  # sitio para las etiquetas
    ejes_todos[0].set_ylabel("nodos expandidos (mediana, escala log)")
    ejes_todos[0].legend(loc="lower right", fontsize=9)
    figura.suptitle("E2 · Nodos expandidos frente a la profundidad (banda: cuartiles 25–75 %)",
                    fontsize=11, x=0.01, ha="left")
    figura.tight_layout()
    guardar(figura, "e2_nodos_vs_d")


def tabla_b_estrella(e2, tipo):
    """Tabla estilo figura 3.26: generados medios y b* medio por intervalo de d."""
    datos = agrupar_por_d(e2[e2.terreno == tipo])
    algoritmos = ["UCS", "A* (h1)", "A* (h2)"]
    media = datos.groupby(["d_grupo", "algoritmo"])[["generados", "b_estrella"]].mean().unstack()
    casos = datos[datos.algoritmo == "UCS"].groupby("d_grupo").size()

    lineas = [
        r"\begin{tabular}{lr|rrr|rrr}",
        r"\hline",
        r" & & \multicolumn{3}{c|}{Nodos generados} & \multicolumn{3}{c}{$b^*$} \\",
        r"$d$ & casos & UCS & A*($h_1$) & A*($h_2$) & UCS & A*($h_1$) & A*($h_2$) \\",
        r"\hline",
    ]
    for d_grupo in media.index:
        if casos[d_grupo] < MIN_CASOS:
            continue
        lo = int(d_grupo - 9.5)
        fila = [f"{lo}--{lo + 19}", str(casos[d_grupo])]
        fila += [f"{media['generados', a][d_grupo]:,.0f}".replace(",", r"\,") for a in algoritmos]
        fila += [f"{media['b_estrella', a][d_grupo]:.3f}" for a in algoritmos]
        lineas.append(" & ".join(fila) + r" \\")
    lineas += [r"\hline", r"\end{tabular}"]
    omitidos = casos[casos < MIN_CASOS].sum()
    if omitidos:
        lineas.append(f"% omitidos {omitidos} casos en intervalos con menos de {MIN_CASOS}")

    ruta = RESULTADOS / f"tabla_b_estrella_{tipo}.tex"
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"  results/{ruta.name}")


def fig_e3(e3):
    """Dos graficas (no doble eje): sobrecoste medio y nodos expandidos medios."""
    orden = ["A* (h2)", "Voraz (h2)", "Voraz (h1)"]
    figura, ejes_todos = plt.subplots(2, 2, figsize=(10, 4.2))
    for columna, (tipo, titulo) in enumerate(TERRENOS.items()):
        media = e3[e3.terreno == tipo].groupby("algoritmo")[["sobrecoste_pct", "expandidos"]].mean().loc[orden]
        y = np.arange(len(orden))
        colores = [COLOR["A* (h2)"] if a == "A* (h2)" else NEUTRO for a in orden]

        for fila, (columna_datos, etiqueta, formato) in enumerate([
                ("sobrecoste_pct", "sobrecoste medio (%)", "{:.1f} %"),
                ("expandidos", "nodos expandidos (media)", "{:,.0f}")]):
            ejes = ejes_todos[fila, columna]
            valores = media[columna_datos]
            ejes.barh(y, valores, color=colores, height=0.6)
            for yi, v in zip(y, valores):
                ejes.annotate(formato.format(v).replace(",", " "), (v, yi), xytext=(4, 0),
                              textcoords="offset points", va="center", fontsize=8, color=TINTA)
            ejes.set_yticks(y, orden if columna == 0 else [""] * len(orden))
            ejes.invert_yaxis()
            ejes.grid(axis="y", visible=False)
            ejes.set_title(f"{titulo} · {etiqueta}", fontsize=10, loc="left")
            ejes.set_xlim(right=valores.max() * 1.25)
    figura.suptitle("E3 · Búsqueda voraz frente al óptimo A*(h2) (30 mapas por terreno)",
                    fontsize=11, x=0.01, ha="left")
    figura.tight_layout()
    guardar(figura, "e3_voraz")


def fig_e4(e4):
    """Diferencia ida/vuelta (%) frente al desnivel S -> G."""
    figura, ejes_todos = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
    for ejes, (tipo, titulo) in zip(ejes_todos, TERRENOS.items()):
        datos = e4[e4.terreno == tipo]
        r = datos[["desnivel_SG", "diferencia_pct"]].corr().iloc[0, 1]
        ejes.axhline(0, color="#8a8984", linewidth=0.8)
        ejes.axvline(0, color="#8a8984", linewidth=0.8)
        misma = datos.misma_ruta
        ejes.scatter(datos.desnivel_SG[misma], datos.diferencia_pct[misma], s=36,
                     color=COLOR["UCS"], edgecolor="white", linewidth=1, label="misma ruta a la vuelta")
        ejes.scatter(datos.desnivel_SG[~misma], datos.diferencia_pct[~misma], s=40, marker="^",
                     facecolor="white", edgecolor=COLOR["UCS"], linewidth=1.5, label="ruta distinta")
        ejes.set_title(f"{titulo}  (r = {r:.2f})", fontsize=11, loc="left")
        ejes.set_xlabel("desnivel h(G) − h(S)  [m]")
    ejes_todos[0].set_ylabel("coste ida / coste vuelta − 1  (%)")
    ejes_todos[0].legend(loc="upper left", fontsize=9)
    figura.suptitle("E4 · Asimetría: ir a un punto más alto cuesta más que volver",
                    fontsize=11, x=0.01, ha="left")
    figura.tight_layout()
    guardar(figura, "e4_asimetria")


def fig_e5(e5):
    """Tiempo, nodos expandidos y frontera maxima frente a N (log-log)."""
    metricas = [("tiempo", "tiempo de búsqueda (s)"), ("expandidos", "nodos expandidos"),
                ("frontera_max", "frontera máxima (memoria)")]
    figura, ejes_todos = plt.subplots(1, 3, figsize=(12, 3.8))
    media = e5.groupby(["algoritmo", "N"])[[m for m, _ in metricas]].mean()
    for ejes, (metrica, titulo) in zip(ejes_todos, metricas):
        for algoritmo, color in COLOR.items():
            serie = media.loc[algoritmo, metrica]
            ejes.plot(serie.index, serie.values, color=color, marker="o", markersize=5, label=algoritmo)
            etiqueta_final(ejes, serie.index[-1], serie.values[-1], algoritmo, color)
        ejes.set_xscale("log", base=2)
        ejes.set_yscale("log")
        ejes.set_xticks(sorted(e5.N.unique()), [str(n) for n in sorted(e5.N.unique())])
        ejes.minorticks_off()
        ejes.set_xlim(right=ejes.get_xlim()[1] * 2.2)
        ejes.set_xlabel("N (mapa N × N)")
        ejes.set_title(titulo, fontsize=11, loc="left")
    ejes_todos[0].legend(loc="upper left", fontsize=9)
    figura.suptitle("E5 · Escalabilidad (media de 20 mapas por tamaño, escalas log)",
                    fontsize=11, x=0.01, ha="left")
    figura.tight_layout()
    guardar(figura, "e5_escalabilidad")


def tabla_e1(e1):
    resumen = e1.groupby(["terreno", "algoritmo"]).agg(
        mapas=("semilla", "nunique"), error_max=("error_relativo", "max"))
    lineas = [r"\begin{tabular}{llrr}", r"\hline",
              r"Terreno & Algoritmo & Mapas & Error relativo máx. \\", r"\hline"]
    for (tipo, algoritmo), fila in resumen.iterrows():
        lineas.append(f"{tipo} & {algoritmo} & {fila.mapas} & {fila.error_max:.1e}" + r" \\")
    lineas += [r"\hline", r"\end{tabular}"]
    (RESULTADOS / "tabla_e1.tex").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print("  results/tabla_e1.tex")


def resumen(e1, e2, e3, e4, e5):
    """Numeros clave para el texto de la memoria."""
    print("\nResumen:")
    print(f"  E1: error relativo maximo frente a networkx = {e1.error_relativo.max():.1e}")
    exp = e2.groupby(["terreno", "algoritmo"]).expandidos.mean().unstack()
    for tipo in TERRENOS:
        print(f"  E2 {tipo}: expandidos medios UCS {exp.loc[tipo, 'UCS']:.0f}, "
              f"A*(h1) {exp.loc[tipo, 'A* (h1)']:.0f}, A*(h2) {exp.loc[tipo, 'A* (h2)']:.0f}")
    sc = e3.groupby(["terreno", "algoritmo"]).sobrecoste_pct.agg(["mean", "max"])
    for tipo in TERRENOS:
        print(f"  E3 {tipo}: voraz(h2) +{sc.loc[(tipo, 'Voraz (h2)'), 'mean']:.1f}% de media "
              f"(max +{sc.loc[(tipo, 'Voraz (h2)'), 'max']:.1f}%)")
    for tipo in TERRENOS:
        d = e4[e4.terreno == tipo]
        print(f"  E4 {tipo}: |ida/vuelta - 1| medio {d.diferencia_pct.abs().mean():.1f}%, "
              f"max {d.diferencia_pct.abs().max():.1f}%, misma ruta en {100 * d.misma_ruta.mean():.0f}%, "
              f"r(desnivel, diferencia) = {d[['desnivel_SG', 'diferencia_pct']].corr().iloc[0, 1]:.2f}")
    t = e5.groupby(["N", "algoritmo"]).tiempo.mean().unstack()
    print(f"  E5 N=400: UCS {t.loc[400, 'UCS']:.2f} s, A*(h2) {t.loc[400, 'A* (h2)']:.2f} s "
          f"({t.loc[400, 'UCS'] / t.loc[400, 'A* (h2)']:.1f}x mas rapido)")


if __name__ == "__main__":
    e1, e2, e3, e4, e5 = (pd.read_csv(RESULTADOS / f) for f in [
        "e1_correccion.csv", "e2_heuristicas.csv", "e3_voraz.csv",
        "e4_asimetria.csv", "e5_escalabilidad.csv"])
    print("Figuras y tablas:")
    fig_velocidad()
    fig_e2(e2)
    tabla_b_estrella(e2, "base")
    tabla_b_estrella(e2, "abrupto")
    fig_e3(e3)
    fig_e4(e4)
    fig_e5(e5)
    tabla_e1(e1)
    resumen(e1, e2, e3, e4, e5)
