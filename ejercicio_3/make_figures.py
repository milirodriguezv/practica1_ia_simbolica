"""
make_figures.py
---------------
Lee results/*.csv (de run_experiments.py) y genera las figuras y tablas:

    figures/velocidad_pendiente.pdf    v(theta), para explicar el modelo de coste
    figures/nodos_por_profundidad.pdf  nodos expandidos frente a d (UCS, A* h1, A* h2)
    figures/voraz.pdf                  tiempo de viaje extra y nodos de la voraz frente a A*
    figures/ida_y_vuelta.pdf           diferencia ida/vuelta frente al desnivel S -> G
    figures/pendiente_maxima.pdf       rutas posibles y tiempo extra segun la pendiente maxima
    results/tabla_b_estrella_*.tex     nodos generados y b* frente a d

Las figuras se guardan en .pdf, para incluirlas en LaTeX.
Las rutas sobre el mapa las dibuja main.py.

Cada algoritmo tiene siempre el mismo color (el de visualizar_terreno.py).
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
from visualizar_terreno import COLOR_ALGORITMO

CARPETA = Path(__file__).parent
RESULTADOS = CARPETA / "results"
FIGURAS = CARPETA / "figures"

COLOR = COLOR_ALGORITMO
COLOR_TERRENO = {"base": "#c1440e", "abrupto": "#6a4c93"}
NEUTRO = "#7a6f66"
TINTA = "black"
TERRENOS = {"base": "Terreno base", "abrupto": "Terreno abrupto"}

plt.rcParams.update({
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "gray",
    "axes.labelcolor": TINTA,
    "xtick.color": NEUTRO,
    "ytick.color": NEUTRO,
    "axes.grid": True,
    "grid.color": "#e8e2da",
    "grid.linewidth": 0.8,
    "axes.axisbelow": True,
    "lines.linewidth": 2,
    "legend.frameon": False,
})


def guardar(figura, nombre):
    FIGURAS.mkdir(exist_ok=True)
    figura.savefig(FIGURAS / f"{nombre}.pdf", bbox_inches="tight")
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
    ejes.plot(grados, v, color=COLOR["A* (h2)"])
    ejes.axvline(0, color="gray", linewidth=0.8)
    limite = math.degrees(THETA_MAX)
    for g, texto in [(-limite, f"bajada: {1 - K_BAJ:.1f}·v_max"), (limite, f"subida: {1 - K_SUB:.1f}·v_max")]:
        valor = velocidad(math.radians(g)) / V_MAX
        ejes.plot(g, valor, "o", color=COLOR["A* (h2)"], markersize=6)
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


def fig_nodos_por_profundidad(heuristicas):
    """Nodos expandidos frente a d: mediana y rango intercuartilico."""
    heuristicas = agrupar_por_d(heuristicas)
    casos = heuristicas[heuristicas.algoritmo == "UCS"].groupby(["terreno", "d_grupo"]).size()
    validos = casos[casos >= MIN_CASOS].index
    heuristicas = heuristicas[heuristicas.set_index(["terreno", "d_grupo"]).index.isin(validos)]
    figura, ejes_todos = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
    for ejes, (tipo, titulo) in zip(ejes_todos, TERRENOS.items()):
        datos = heuristicas[heuristicas.terreno == tipo]
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
    figura.suptitle("Nodos expandidos frente a la profundidad de la solución (banda: cuartiles 25–75 %)",
                    fontsize=11, x=0.01, ha="left")
    figura.tight_layout()
    guardar(figura, "nodos_por_profundidad")


def tabla_b_estrella(heuristicas, tipo):
    """Tabla estilo figura 3.26: generados medios y b* medio por intervalo de d."""
    datos = agrupar_por_d(heuristicas[heuristicas.terreno == tipo])
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


def fig_voraz(voraz):
    """Dos graficas por terreno: tiempo de viaje extra medio y nodos expandidos medios."""
    orden = ["A* (h2)", "Voraz (h2)", "Voraz (h1)"]
    figura, ejes_todos = plt.subplots(2, 2, figsize=(10, 4.2))
    for columna, (tipo, titulo) in enumerate(TERRENOS.items()):
        media = voraz[voraz.terreno == tipo].groupby("algoritmo")[["sobrecoste_pct", "expandidos"]].mean().loc[orden]
        y = np.arange(len(orden))
        colores = [COLOR["A* (h2)"] if a == "A* (h2)" else NEUTRO for a in orden]

        for fila, (columna_datos, etiqueta, formato) in enumerate([
                ("sobrecoste_pct", "tiempo de viaje extra (%)", "{:.1f} %"),
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
    figura.suptitle("Búsqueda voraz frente a la ruta óptima de A*(h2) (30 mapas por terreno)",
                    fontsize=11, x=0.01, ha="left")
    figura.tight_layout()
    guardar(figura, "voraz")


def fig_ida_y_vuelta(ida_y_vuelta):
    """Diferencia ida/vuelta (%) frente al desnivel S -> G."""
    figura, ejes_todos = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
    for ejes, (tipo, titulo) in zip(ejes_todos, TERRENOS.items()):
        datos = ida_y_vuelta[ida_y_vuelta.terreno == tipo]
        r = datos[["desnivel_SG", "diferencia_pct"]].corr().iloc[0, 1]
        ejes.axhline(0, color="gray", linewidth=0.8)
        ejes.axvline(0, color="gray", linewidth=0.8)
        misma = datos.misma_ruta
        ejes.scatter(datos.desnivel_SG[misma], datos.diferencia_pct[misma], s=36,
                     color=COLOR_TERRENO[tipo], edgecolor="white", linewidth=1, label="misma ruta a la vuelta")
        ejes.scatter(datos.desnivel_SG[~misma], datos.diferencia_pct[~misma], s=40, marker="^",
                     facecolor="white", edgecolor=COLOR_TERRENO[tipo], linewidth=1.5, label="ruta distinta")
        ejes.set_title(f"{titulo}  (r = {r:.2f})", fontsize=11, loc="left")
        ejes.set_xlabel("desnivel h(G) − h(S)  [m]")
    ejes_todos[0].set_ylabel("coste ida / coste vuelta − 1  (%)")
    ejes_todos[0].legend(loc="upper left", fontsize=9)
    figura.suptitle("Ida y vuelta: ir a un punto más alto cuesta más que volver",
                    fontsize=11, x=0.01, ha="left")
    figura.tight_layout()
    guardar(figura, "ida_y_vuelta")


def mapas_con_ruta_siempre(datos):
    """Filas de los mapas en los que hay ruta con todas las pendientes
    maximas. Para comparar tiempos hay que usar siempre los mismos mapas;
    si no, cada media saldria de un conjunto de mapas distinto."""
    siempre = datos.groupby(["terreno", "semilla"]).hay_ruta.transform("all")
    return datos[siempre]


def fig_pendiente_maxima(datos):
    """Izquierda: en cuantos mapas sigue habiendo ruta. Derecha: cuanto se
    alarga el viaje respecto al rover que aguanta 25 grados, en los mapas
    en los que todos los rovers llegan."""
    comparables = mapas_con_ruta_siempre(datos)
    figura, (izquierda, derecha) = plt.subplots(1, 2, figsize=(10, 3.6))
    for tipo, titulo in TERRENOS.items():
        del_tipo = datos[datos.terreno == tipo]
        por_pendiente = del_tipo.groupby("theta_max_grados")
        con_ruta = 100 * por_pendiente.hay_ruta.mean()
        tiempo_extra = comparables[comparables.terreno == tipo].groupby(
            "theta_max_grados").tiempo_extra_pct.mean()
        izquierda.plot(con_ruta.index, con_ruta.values, marker="o", color=COLOR_TERRENO[tipo], label=titulo)
        derecha.plot(tiempo_extra.index, tiempo_extra.values, marker="o", color=COLOR_TERRENO[tipo], label=titulo)

    pendientes = sorted(datos.theta_max_grados.unique())
    for ejes in (izquierda, derecha):
        ejes.set_xticks(pendientes, [f"{g}°" for g in pendientes])
        ejes.set_xlabel("pendiente máxima que aguanta el rover")
    izquierda.set_ylabel("mapas en los que hay ruta (%)")
    izquierda.set_ylim(0, 105)
    izquierda.set_title("¿Se puede llegar a G?", fontsize=11, loc="left")
    derecha.set_ylabel("tiempo de viaje extra (%)")
    derecha.set_title("Cuánto se alarga el viaje (mapas donde todos llegan)", fontsize=11, loc="left")
    izquierda.legend(loc="lower right", fontsize=9)
    figura.suptitle("Rovers que aguantan menos pendiente (mismos mapas, mismo S y G)",
                    fontsize=11, x=0.01, ha="left")
    figura.tight_layout()
    guardar(figura, "pendiente_maxima")


def resumen(heuristicas, voraz, ida_y_vuelta, pendiente):
    """Numeros clave para el texto de la memoria."""
    print("\nResumen:")
    exp = heuristicas.groupby(["terreno", "algoritmo"]).expandidos.mean().unstack()
    for tipo in TERRENOS:
        print(f"  heuristicas, {tipo}: expandidos medios UCS {exp.loc[tipo, 'UCS']:.0f}, "
              f"A*(h1) {exp.loc[tipo, 'A* (h1)']:.0f}, A*(h2) {exp.loc[tipo, 'A* (h2)']:.0f}")
    sc = voraz.groupby(["terreno", "algoritmo"]).sobrecoste_pct.agg(["mean", "max"])
    for tipo in TERRENOS:
        print(f"  voraz, {tipo}: voraz(h2) +{sc.loc[(tipo, 'Voraz (h2)'), 'mean']:.1f}% de media "
              f"(max +{sc.loc[(tipo, 'Voraz (h2)'), 'max']:.1f}%)")
    for tipo in TERRENOS:
        d = ida_y_vuelta[ida_y_vuelta.terreno == tipo]
        print(f"  ida y vuelta, {tipo}: |ida/vuelta - 1| medio {d.diferencia_pct.abs().mean():.1f}%, "
              f"max {d.diferencia_pct.abs().max():.1f}%, misma ruta en {100 * d.misma_ruta.mean():.0f}%, "
              f"r(desnivel, diferencia) = {d[['desnivel_SG', 'diferencia_pct']].corr().iloc[0, 1]:.2f}")
    comparables = mapas_con_ruta_siempre(pendiente)
    for tipo in TERRENOS:
        del_tipo = pendiente[pendiente.terreno == tipo]
        comparables_tipo = comparables[comparables.terreno == tipo]
        for grados in sorted(pendiente.theta_max_grados.unique()):
            hay_ruta = del_tipo[del_tipo.theta_max_grados == grados].hay_ruta
            extra = comparables_tipo[comparables_tipo.theta_max_grados == grados].tiempo_extra_pct
            print(f"  pendiente maxima {grados} grados, {tipo}: hay ruta en {100 * hay_ruta.mean():.0f}% "
                  f"de los mapas, tiempo extra medio {extra.mean():.1f}% (max {extra.max():.1f}%)")


if __name__ == "__main__":
    heuristicas = pd.read_csv(RESULTADOS / "heuristicas.csv")
    voraz = pd.read_csv(RESULTADOS / "voraz.csv")
    ida_y_vuelta = pd.read_csv(RESULTADOS / "ida_y_vuelta.csv")
    pendiente = pd.read_csv(RESULTADOS / "pendiente_maxima.csv")

    print("Figuras y tablas:")
    fig_velocidad()
    fig_nodos_por_profundidad(heuristicas)
    tabla_b_estrella(heuristicas, "base")
    tabla_b_estrella(heuristicas, "abrupto")
    fig_voraz(voraz)
    fig_ida_y_vuelta(ida_y_vuelta)
    fig_pendiente_maxima(pendiente)
    resumen(heuristicas, voraz, ida_y_vuelta, pendiente)
