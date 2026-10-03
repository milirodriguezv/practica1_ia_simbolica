"""
Experimentos

Uso:
    python main.py          -> ejecuta todos los experimentos
    python main.py auditoria  -> ejecuta solo ese experimento

Experimentos: clasificacion, subsuncion, cambio_del_pecorino, consistencia,
auditoria y menus_para_clientes. Antes de cualquiera se valida la ontologia.

Cada uno imprime sus resultados y los guarda en resultados/<nombre>.md
(la auditoria guarda ademas la figura resultados/auditoria.pdf).
"""

import copy
import os
import sys

import matplotlib
matplotlib.use("Agg")  # para poder generar la imagen sin pantalla
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from ontologia import ONTOLOGIA
from carta import CARTA
import razonador

# Los resultados usan simbolos de logica descriptiva (≡, ⊑, ⊓, ∀...). En
# Windows la consola puede no estar en UTF-8 y print() fallaria con
# UnicodeEncodeError, asi que se fuerza UTF-8 en la salida.
sys.stdout.reconfigure(encoding="utf-8")

CARPETA = "resultados"


def guardar(nombre, lineas):
    """Imprime las lineas y las guarda en resultados/<nombre>.md"""
    texto = "\n".join(lineas)
    print(texto)
    print()
    os.makedirs(CARPETA, exist_ok=True)
    with open(os.path.join(CARPETA, nombre + ".md"), "w", encoding="utf-8") as f:
        f.write(texto + "\n")


# Validacion de la ontologia
def validacion():
    lineas = ["# Validacion de la ontologia", ""]
    errores = razonador.validar_ontologia(ONTOLOGIA, CARTA)
    if len(errores) == 0:
        lineas.append(f"Ontologia valida: {len(ONTOLOGIA['taxonomia'])} clases, "
                      f"{len(razonador.hojas(ONTOLOGIA))} ingredientes atomicos, "
                      f"{len(CARTA['compuestos'])} elaborados, "
                      f"{len(CARTA['platos'])} platos, "
                      f"{len(ONTOLOGIA['categorias'])} categorias.")
        lineas.append("")
        lineas.append("Definiciones de las categorias (TBox):")
        lineas.append("")
        lineas.append("- PlatoValido ≡ Plato ⊓ ∃contiene.Ingrediente")
        for nombre, datos in ONTOLOGIA["categorias"].items():
            lineas.append(f"- {nombre} ≡ {datos['formula']}")
    else:
        lineas.append("Se han encontrado errores:")
        for error in errores:
            lineas.append("- " + error)
    guardar("validacion", lineas)
    return len(errores) == 0


# Clasificacion de la carta
def clasificacion():
    categorias = list(ONTOLOGIA["categorias"])
    lineas = ["# Clasificacion de la carta", ""]

    # Tabla plato x categoria
    lineas.append("| Plato | Tipo | " + " | ".join(categorias) + " |")
    lineas.append("|---|---|" + "---|" * len(categorias))
    justificaciones = []
    for plato, datos in CARTA["platos"].items():
        cumple, motivos = razonador.clasificar(plato, ONTOLOGIA, CARTA)
        celdas = []
        for categoria in categorias:
            if categoria in cumple:
                celdas.append("✓")
            else:
                celdas.append("✗")
        lineas.append(f"| {plato} | {datos['tipo']} | " + " | ".join(celdas) + " |")

        for categoria, violaciones in motivos.items():
            for v in violaciones:
                justificaciones.append(f"- {plato} no es {categoria}: "
                                       + razonador.texto_violacion(v))

    lineas.append("")
    lineas.append("## Justificaciones (por que NO cumple)")
    lineas.append("")
    lineas = lineas + justificaciones
    guardar("clasificacion", lineas)


# Subsuncion entre categorias
def subsuncion():
    lineas = ["# Subsuncion entre categorias (comparando definiciones)", ""]
    lineas.append("| C | D | ¿C ⊑ D? | Contraejemplo |")
    lineas.append("|---|---|---|---|")
    positivas = []
    for r in razonador.jerarquia_categorias(ONTOLOGIA):
        if r["subsume"]:
            positivas.append(f"{r['c']} ⊑ {r['d']}")
            lineas.append(f"| {r['c']} | {r['d']} | Si | - |")
        else:
            lineas.append(f"| {r['c']} | {r['d']} | No | plato {{{r['contraejemplo']}}} |")

    lineas.append("")
    lineas.append("Un contraejemplo {h} es un plato hipotetico con un solo "
                  "ingrediente h que cumple C pero no D.")
    lineas.append("")
    lineas.append("Subsunciones inferidas: " + (", ".join(positivas) if positivas else "ninguna"))
    guardar("subsuncion", lineas)


# Que pasa si cambia la TBox: el Pecorino sin lactosa
def cambio_del_pecorino():
    lineas = ["# Cambio en la TBox: el Pecorino como queso sin lactosa", ""]
    lineas.append("Cambio: declarar el PecorinoRomano como queso curado "
                  "sin lactosa (quitar PecorinoRomano ⊑ ConLactosa).")
    lineas.append("")

    # Copia de la ontologia con el cambio (la original no se toca)
    onto_modificada = copy.deepcopy(ONTOLOGIA)
    onto_modificada["taxonomia"]["PecorinoRomano"] = ["Lacteo"]

    hay_cambios = False
    for plato in CARTA["platos"]:
        antes, _ = razonador.clasificar(plato, ONTOLOGIA, CARTA)
        despues, _ = razonador.clasificar(plato, onto_modificada, CARTA)
        if antes != despues:
            hay_cambios = True
            lineas.append(f"- {plato}: {antes} -> {despues}")

    if not hay_cambios:
        lineas.append("No cambia ninguna clasificacion.")

    lineas.append("")
    lineas.append("La carta (ABox) es la misma: el cambio de clasificacion "
                  "viene solo del cambio en el conocimiento general (TBox).")
    guardar("cambio_del_pecorino", lineas)


# Consistencia de conceptos
def consistencia():
    # (categorias, clases que el plato debe contener)
    consultas = [
        (["Vegetariano"], ["Pescado"]),
        (["SinCarne"], ["Pescado"]),
        (["SinLactosa"], ["Lacteo"]),
        (["SinLactosa"], ["Mozzarella"]),
        (["SinGluten"], ["Cereal"]),
        (["SinGluten", "Vegetariano", "SinLactosa"], ["Lacteo"]),
        (["Vegano"], ["Lacteo"]),
        (["Vegano", "SinGluten"], ["Cereal"]),
    ]

    lineas = ["# Consistencia de conceptos", ""]
    lineas.append("| Concepto | ¿Satisfacible? | Testigo / motivo |")
    lineas.append("|---|---|---|")
    for categorias, requiere in consultas:
        partes = categorias + ["∃contiene." + clase for clase in requiere]
        concepto = " ⊓ ".join(partes)
        ok, detalle = razonador.es_satisfacible(categorias, requiere, ONTOLOGIA)
        if ok:
            lineas.append(f"| {concepto} | Si | plato {{{', '.join(detalle)}}} |")
        else:
            lineas.append(f"| {concepto} | No | {detalle} |")
    guardar("consistencia", lineas)


# ------------------------------------------------------------------
# Auditoria de la carta
# ------------------------------------------------------------------
def auditoria():
    lineas = ["# Auditoria de las etiquetas de la carta", ""]
    discrepancias = razonador.auditar_carta(ONTOLOGIA, CARTA)
    if len(discrepancias) == 0:
        lineas.append("La carta coincide exactamente con lo inferido.")
    for d in discrepancias:
        if d["tipo"] == "ETIQUETA FALSA":
            motivo = "; ".join(razonador.texto_violacion(v) for v in d["motivo"])
            if motivo == "":
                motivo = "el plato no tiene ingredientes"
            lineas.append(f"- [ETIQUETA FALSA] {d['plato']} dice ser "
                          f"{d['categoria']}, pero: {motivo}")
        else:
            lineas.append(f"- [OMISION] {d['plato']} es {d['categoria']} "
                          "y la carta no lo indica")
    guardar("auditoria", lineas)
    dibujar_carta(discrepancias)


# Colores de la figura: verde albahaca si el plato cumple la categoria,
# crema si no, borde rojo tomate para una etiqueta falsa y borde amarillo
# (aceite) para una omision.
VERDE_ALBAHACA = "#5b8c3a"
CREMA = "#f3ecdc"
ROJO_TOMATE = "#c8332b"
AMARILLO_ACEITE = "#d9a400"


def dibujar_carta(discrepancias):
    """Tabla platos x categorias. El color de fondo es lo que infiere el
    razonador y la palabra "carta" indica lo que dice la carta impresa."""
    platos = list(CARTA["platos"])
    categorias = list(ONTOLOGIA["categorias"])
    figura, ejes = plt.subplots(figsize=(7.2, 4.6))

    for fila, plato in enumerate(platos):
        cumple, _ = razonador.clasificar(plato, ONTOLOGIA, CARTA)
        for columna, categoria in enumerate(categorias):
            color = VERDE_ALBAHACA if categoria in cumple else CREMA
            ejes.add_patch(Rectangle((columna, fila), 1, 1, facecolor=color,
                                     edgecolor="white", linewidth=2))
            if categoria in CARTA["platos"][plato]["etiquetas_carta"]:
                ejes.text(columna + 0.5, fila + 0.5, "carta", ha="center", va="center",
                          fontsize=7, color="white" if categoria in cumple else "dimgray")

    # recuadros sobre las celdas donde la carta y el razonador no coinciden
    for d in discrepancias:
        fila = platos.index(d["plato"])
        columna = categorias.index(d["categoria"])
        if d["tipo"] == "ETIQUETA FALSA":
            borde, trazo = ROJO_TOMATE, "-"
        else:
            borde, trazo = AMARILLO_ACEITE, "--"
        ejes.add_patch(Rectangle((columna + 0.05, fila + 0.05), 0.9, 0.9, fill=False,
                                 edgecolor=borde, linestyle=trazo, linewidth=2.5))

    ejes.set_xlim(0, len(categorias))
    ejes.set_ylim(len(platos), 0)
    ejes.set_xticks([c + 0.5 for c in range(len(categorias))], categorias, fontsize=9)
    ejes.set_yticks([f + 0.5 for f in range(len(platos))], platos, fontsize=8)
    ejes.xaxis.tick_top()
    ejes.tick_params(length=0)
    for lado in ejes.spines.values():
        lado.set_visible(False)

    leyenda = [
        Rectangle((0, 0), 1, 1, facecolor=VERDE_ALBAHACA, label="cumple"),
        Rectangle((0, 0), 1, 1, facecolor=CREMA, edgecolor="lightgray", label="no cumple"),
        Rectangle((0, 0), 1, 1, fill=False, edgecolor=ROJO_TOMATE, linewidth=2, label="etiqueta falsa"),
        Rectangle((0, 0), 1, 1, fill=False, edgecolor=AMARILLO_ACEITE, linestyle="--", label="omisión"),
    ]
    ejes.legend(handles=leyenda, loc="upper center", bbox_to_anchor=(0.45, -0.02),
                ncol=4, fontsize=8, frameon=False)
    figura.tight_layout()
    figura.savefig(os.path.join(CARPETA, "auditoria.pdf"))
    plt.close(figura)


# ------------------------------------------------------------------
# Menus para clientes con restricciones
# ------------------------------------------------------------------
# cliente -> categorias que debe cumplir todo lo que pida
CLIENTES = {
    "Celiaco": ["SinGluten"],
    "Vegetariano": ["Vegetariano"],
    "Intolerante a la lactosa": ["SinLactosa"],
    "Vegano": ["Vegano"],
    "Celiaco y vegetariano": ["SinGluten", "Vegetariano"],
    "Celiaco e intolerante a la lactosa": ["SinGluten", "SinLactosa"],
}


def platos_aptos(categorias, tipo, segun_la_carta=False):
    """Platos de un tipo (Entrante, Principal o Postre) que cumplen todas
    las categorias. Con segun_la_carta=True se miran las etiquetas
    impresas en la carta en vez de lo que infiere el razonador."""
    aptos = []
    for plato, datos in CARTA["platos"].items():
        if datos["tipo"] != tipo:
            continue
        if segun_la_carta:
            cumple = datos["etiquetas_carta"]
        else:
            cumple, _ = razonador.clasificar(plato, ONTOLOGIA, CARTA)
        if all(categoria in cumple for categoria in categorias):
            aptos.append(plato)
    return aptos


def menus_para_clientes():
    """Para cada cliente, que puede pedir de entrante, principal y postre,
    y si le sale un menu completo. Ademas se avisa de los platos que la
    carta impresa le ofreceria y que en realidad no puede comer."""
    tipos = ONTOLOGIA["tipos_plato"]
    lineas = ["# Menus para clientes con restricciones", ""]
    lineas.append("| Cliente | " + " | ".join(tipos) + " | ¿Menu completo? |")
    lineas.append("|---|" + "---|" * (len(tipos) + 1))

    avisos = []
    for cliente, categorias in CLIENTES.items():
        celdas = []
        completo = True
        for tipo in tipos:
            aptos = platos_aptos(categorias, tipo)
            if len(aptos) == 0:
                completo = False
                celdas.append("ninguno")
            else:
                celdas.append(", ".join(aptos))

            # platos que la carta impresa anuncia como aptos y no lo son
            for plato in platos_aptos(categorias, tipo, segun_la_carta=True):
                if plato not in aptos:
                    avisos.append(f"- {cliente}: la carta le ofrece {plato}, pero no es apto")

        lineas.append(f"| {cliente} | " + " | ".join(celdas)
                      + f" | {'Si' if completo else 'No'} |")

    lineas.append("")
    lineas.append("## Platos que la carta ofrece por error")
    lineas.append("")
    if len(avisos) == 0:
        lineas.append("Ninguno.")
    lineas = lineas + avisos
    guardar("menus_para_clientes", lineas)


EXPERIMENTOS = {
    "clasificacion": clasificacion,
    "subsuncion": subsuncion,
    "cambio_del_pecorino": cambio_del_pecorino,
    "consistencia": consistencia,
    "auditoria": auditoria,
    "menus_para_clientes": menus_para_clientes,
}


if __name__ == "__main__":
    # Si la ontologia no es valida, no tiene sentido razonar sobre ella
    if not validacion():
        sys.exit(1)

    if len(sys.argv) > 1:
        nombre = sys.argv[1]
        if nombre not in EXPERIMENTOS:
            print(f"Experimento desconocido: {nombre}. "
                  f"Opciones: {', '.join(EXPERIMENTOS)}")
            sys.exit(1)
        EXPERIMENTOS[nombre]()
    else:
        for experimento in EXPERIMENTOS.values():
            experimento()
