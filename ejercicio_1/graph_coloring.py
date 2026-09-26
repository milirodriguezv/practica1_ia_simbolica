"""
graph_coloring.py
------------------
Funciones puras que traducen "colorear un grafo" al lenguaje que
entienden KnowledgeBase y DPLLSolver: una lista de clausulas FNC.

Ahora es el propio Environment quien llama a estas funciones (ver
environment.py, metodo traducir_a_clausulas()). Este archivo no sabe
nada de agentes ni de KB: solo hace la traduccion.

Idea de la codificacion (variable = numero entero, como siempre):
    Por cada region R y cada color C, creamos una variable booleana
    que preguntamos: "la region R tiene el color C?"

Reglas (clausulas) que hacen falta:
    1) Cada region tiene AL MENOS un color
       (region=color1 OR region=color2 OR ... )
    2) Cada region tiene A LO SUMO un color
       (no puede tener dos colores a la vez)
    3) Dos regiones vecinas NO pueden tener el mismo color
"""


def crear_variables(regiones, colores):
    """Asigna un numero de variable distinto a cada par (region, color)."""
    variable_id = {}
    contador = 1
    for region in regiones:
        for color in colores:
            variable_id[(region, color)] = contador
            contador += 1
    return variable_id


def generar_clausulas(regiones, colores, adyacencias, variable_id):
    clausulas = []

    # regla 1: cada region tiene al menos un color
    for region in regiones:
        clausula = set()
        for color in colores:
            var = variable_id[(region, color)]
            clausula.add(var)
        clausulas.append(clausula)

    # regla 2: cada region tiene a lo sumo un color
    # (para cada par de colores distintos, no pueden ser ambos verdaderos)
    for region in regiones:
        for i in range(len(colores)):
            for j in range(i + 1, len(colores)):
                color_i = colores[i]
                color_j = colores[j]
                var_i = variable_id[(region, color_i)]
                var_j = variable_id[(region, color_j)]
                clausulas.append({-var_i, -var_j})

    # regla 3: regiones vecinas no pueden compartir color
    for (region_a, region_b) in adyacencias:
        for color in colores:
            var_a = variable_id[(region_a, color)]
            var_b = variable_id[(region_b, color)]
            clausulas.append({-var_a, -var_b})

    return clausulas
