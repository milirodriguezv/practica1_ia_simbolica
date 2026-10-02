"""
Experimentos

Uso:
    python main.py          -> ejecuta todos los experimentos
    python main.py E3       -> ejecuta solo el experimento E3

Cada experimento imprime sus resultados y los guarda en resultados/EX.md
"""

import copy
import os
import random
import sys

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


# E0. Validacion de la ontologia
def e0_validacion():
    lineas = ["# E0. Validacion de la ontologia", ""]
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
    guardar("E0_validacion", lineas)
    return len(errores) == 0


# E1. Clasificacion de la carta
def e1_clasificacion():
    categorias = list(ONTOLOGIA["categorias"])
    lineas = ["# E1. Clasificacion de la carta", ""]

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
    guardar("E1_clasificacion", lineas)


# E2. Subsuncion entre categorias
def e2_subsuncion():
    lineas = ["# E2. Subsuncion entre categorias (comparando definiciones)", ""]
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
    guardar("E2_subsuncion", lineas)


# E3. Sensibilidad a la TBox (ablacion)
def e3_ablacion():
    lineas = ["# E3. Sensibilidad a la TBox", ""]
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
    guardar("E3_ablacion", lineas)


# E4. Consistencia de conceptos
def e4_consistencia():
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

    lineas = ["# E4. Consistencia de conceptos", ""]
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
    guardar("E4_consistencia", lineas)


# ------------------------------------------------------------------
# E5. Auditoria de la carta
# ------------------------------------------------------------------
def e5_auditoria():
    lineas = ["# E5. Auditoria de las etiquetas de la carta", ""]
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
    guardar("E5_auditoria", lineas)


# ------------------------------------------------------------------
# E6. Comprobacion de la subsuncion con platos aleatorios
# ------------------------------------------------------------------
def comprobar_subsunciones(n_platos=10000, semilla=0):
    """Contrasta subsume() (que compara definiciones) con clasificar()
    (que mira los ingredientes de cada plato) sobre platos aleatorios de
    1 a 5 ingredientes atomicos:
      - si C ⊑ D, ningun plato de C puede quedar fuera de D;
      - si C no ⊑ D, deberia aparecer algun plato de C fuera de D.
    Devuelve una fila por pareja (C, D)."""
    rng = random.Random(semilla)
    ingredientes = sorted(razonador.hojas(ONTOLOGIA))
    carta = {"compuestos": {}, "platos": {}}

    # Categorias de cada plato aleatorio
    clasificados = []
    for _ in range(n_platos):
        componentes = rng.sample(ingredientes, rng.randint(1, 5))
        carta["platos"]["Aleatorio"] = {"tipo": "Principal", "componentes": componentes,
                                        "etiquetas_carta": []}
        cumple, _ = razonador.clasificar("Aleatorio", ONTOLOGIA, carta)
        clasificados.append(set(cumple))

    filas = []
    for r in razonador.jerarquia_categorias(ONTOLOGIA):
        en_c = [cats for cats in clasificados if r["c"] in cats]
        fuera_de_d = sum(1 for cats in en_c if r["d"] not in cats)
        filas.append({"c": r["c"], "d": r["d"], "subsume": r["subsume"],
                      "platos_en_c": len(en_c), "fuera_de_d": fuera_de_d,
                      "coincide": r["subsume"] == (fuera_de_d == 0)})
    return filas


def e6_comprobacion(n_platos=10000):
    lineas = ["# E6. Comprobacion de la subsuncion con platos aleatorios", ""]
    lineas.append(f"{n_platos} platos aleatorios (1-5 ingredientes atomicos, semilla 0), "
                  "clasificados uno a uno con clasificar().")
    lineas.append("")
    lineas.append("| C | D | Razonador: ¿C ⊑ D? | Platos en C | De ellos, fuera de D | ¿Coincide? |")
    lineas.append("|---|---|---|---|---|---|")
    filas = comprobar_subsunciones(n_platos)
    for f in filas:
        lineas.append(f"| {f['c']} | {f['d']} | {'Si' if f['subsume'] else 'No'} | "
                      f"{f['platos_en_c']} | {f['fuera_de_d']} | {'Si' if f['coincide'] else 'NO'} |")
    lineas.append("")
    lineas.append(f"Coinciden {sum(f['coincide'] for f in filas)} de {len(filas)} parejas.")
    guardar("E6_comprobacion", lineas)


EXPERIMENTOS = {
    "E1": e1_clasificacion,
    "E2": e2_subsuncion,
    "E3": e3_ablacion,
    "E4": e4_consistencia,
    "E5": e5_auditoria,
    "E6": e6_comprobacion,
}


if __name__ == "__main__":
    # Si la ontologia no es valida, no tiene sentido razonar sobre ella
    if not e0_validacion():
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
