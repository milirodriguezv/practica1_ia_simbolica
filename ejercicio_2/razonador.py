"""Razonador sobre categorias para la ontologia del restaurante.

Implementa las siguientes tareas de logica descriptiva:

  - Clasificacion: ¿a que categorias pertenece un plato?
  - Subsuncion:    ¿una categoria esta contenida en otra (C ⊑ D)?
  - Consistencia:  ¿puede existir un plato que cumpla una definicion?

Ademas valida la propia ontologia y audita las etiquetas de la carta.

IMPORTANTE: este fichero no contiene ningun plato ni ingrediente concreto.
Todo el conocimiento llega por parametro:
    onto  -> la TBox (ontologia.py)
    carta -> la ABox (carta.py)

Supuestos de mundo cerrado:
  - la lista de ingredientes de cada plato es completa;
  - los unicos ingredientes que existen son las hojas de la taxonomia.
"""


# 1. Taxonomia: ancestros y hojas

def ancestros(clase, onto):
    """Devuelve la clase y todas sus superclases.

    Es el cierre reflexivo y transitivo de la relacion "es-un" (⊑).
    Funciona como un encadenamiento hacia delante: partimos de la clase
    y vamos anadiendo padres hasta que no aparece ninguno nuevo.

    Args:
        clase: Nombre de la clase.
        onto: La TBox (diccionario ONTOLOGIA).

    Returns:
        Conjunto con la clase y todos sus ancestros.
    """
    taxonomia = onto["taxonomia"]
    encontrados = {clase}
    pendientes = [clase]
    while len(pendientes) > 0:
        actual = pendientes.pop()
        for padre in taxonomia.get(actual, []):
            if padre not in encontrados:
                encontrados.add(padre)
                pendientes.append(padre)
    return encontrados


def hojas(onto):
    """Devuelve las clases que no tienen subclases: los ingredientes atomicos.

    Args:
        onto: La TBox.

    Returns:
        Conjunto de nombres de ingredientes atomicos.
    """
    taxonomia = onto["taxonomia"]
    clases_con_hijos = set()
    for padres in taxonomia.values():
        for padre in padres:
            clases_con_hijos.add(padre)

    resultado = set()
    for clase in taxonomia:
        if clase not in clases_con_hijos:
            resultado.add(clase)
    return resultado


def hojas_bajo(clase, onto):
    """Devuelve los ingredientes atomicos que son de una clase.

    Args:
        clase: Nombre de la clase (p. ej. "Lacteo").
        onto: La TBox.

    Returns:
        Conjunto de ingredientes atomicos que tienen esa clase como ancestro.
    """
    resultado = set()
    for hoja in hojas(onto):
        if clase in ancestros(hoja, onto):
            resultado.add(hoja)
    return resultado


# 2. Relacion "contiene": de un plato a sus ingredientes atomicos

def expandir(nombre, carta, ruta):
    """Baja por los ingredientes elaborados hasta los ingredientes atomicos.

    La ruta dice por donde se ha llegado a cada ingrediente y sirve para
    justificar despues los resultados. Por ejemplo:
        ("Leche", ["HeladoDePistacho", "BaseHelado"])

    Args:
        nombre: Ingrediente atomico o elaborado.
        carta: La ABox (diccionario CARTA).
        ruta: Lista de nombres por los que se ha pasado hasta llegar aqui.

    Returns:
        Lista de pares (ingrediente_atomico, ruta).

    Raises:
        ValueError: Si un elaborado se contiene a si mismo (ciclo).
    """
    compuestos = carta["compuestos"]

    # Caso base: es un ingrediente atomico
    if nombre not in compuestos:
        return [(nombre, ruta)]

    # Si el elaborado ya estaba en la ruta, hay un ciclo (se contiene a si mismo)
    if nombre in ruta:
        raise ValueError("Ciclo en ingredientes compuestos: "
                         + " -> ".join(ruta + [nombre]))

    resultado = []
    for componente in compuestos[nombre]:
        resultado = resultado + expandir(componente, carta, ruta + [nombre])
    return resultado


def ingredientes_de_plato(plato, carta):
    """Devuelve todos los ingredientes atomicos de un plato, con su ruta.

    Args:
        plato: Nombre del plato.
        carta: La ABox.

    Returns:
        Lista de pares (ingrediente_atomico, ruta).
    """
    resultado = []
    for componente in carta["platos"][plato]["componentes"]:
        resultado = resultado + expandir(componente, carta, [plato])
    return resultado


# 3. Validacion de la ontologia (consistencia de la TBox y la ABox)

def validar_ontologia(onto, carta):
    """Comprueba la consistencia de la TBox y de la ABox.

    Revisa que todos los padres esten definidos, que no haya ciclos, que
    se respeten las clases disjuntas y las descomposiciones exhaustivas, y
    que la carta solo use tipos, ingredientes y etiquetas que existen.

    Args:
        onto: La TBox.
        carta: La ABox.

    Returns:
        Lista de mensajes de error. Si esta vacia, la ontologia es valida.
    """
    errores = []
    taxonomia = onto["taxonomia"]
    todas_las_hojas = hojas(onto)

    # 3.1 Todos los padres estan definidos
    for clase, padres in taxonomia.items():
        for padre in padres:
            if padre not in taxonomia:
                errores.append(f"La clase '{padre}' (padre de '{clase}') no esta definida")

    # 3.2 No hay ciclos en la taxonomia (A ⊑ B ⊑ A)
    for clase, padres in taxonomia.items():
        for padre in padres:
            if clase in ancestros(padre, onto):
                errores.append(f"Ciclo en la taxonomia que pasa por '{clase}'")

    # 3.3 Disjuncion: ningun ingrediente esta en dos clases disjuntas
    for hoja in todas_las_hojas:
        sus_clases = ancestros(hoja, onto)
        for grupo in onto["disjuntas"]:
            en_comun = [c for c in grupo if c in sus_clases]
            if len(en_comun) > 1:
                errores.append(f"'{hoja}' pertenece a clases disjuntas: {en_comun}")

    # 3.4 Exhaustividad: todo lo que esta bajo el padre esta bajo algun hijo
    for padre, hijos in onto["exhaustivas"].items():
        for hoja in hojas_bajo(padre, onto):
            sus_clases = ancestros(hoja, onto)
            cubierta = False
            for hijo in hijos:
                if hijo in sus_clases:
                    cubierta = True
            if not cubierta:
                errores.append(f"'{hoja}' es {padre} pero no es ninguno de {hijos}")

    # 3.5 La carta solo usa tipos, ingredientes y etiquetas que existen
    for plato, datos in carta["platos"].items():
        if datos["tipo"] not in onto["tipos_plato"]:
            errores.append(f"'{plato}' tiene un tipo desconocido: {datos['tipo']}")

        for etiqueta in datos["etiquetas_carta"]:
            if etiqueta not in onto["categorias"]:
                errores.append(f"'{plato}' tiene una etiqueta desconocida: {etiqueta}")

        try:
            ingredientes = ingredientes_de_plato(plato, carta)
        except ValueError as error:
            errores.append(str(error))
            continue

        for ingrediente, ruta in ingredientes:
            if ingrediente not in todas_las_hojas:
                errores.append(f"'{ingrediente}' (en {' -> '.join(ruta)}) "
                               "no es un ingrediente atomico de la ontologia")

    return errores


# 4. Clasificacion (nivel de instancia: plato -> categorias)

def comprobar_categoria(plato, categoria, onto, carta):
    """Comprueba si un plato pertenece a una categoria.

    Regla:  plato ∈ C  <=>  tiene al menos un ingrediente
                            y ninguno es de una clase prohibida F(C).

    Args:
        plato: Nombre del plato.
        categoria: Nombre de la categoria (p. ej. "SinGluten").
        onto: La TBox.
        carta: La ABox.

    Returns:
        Tupla (cumple, violaciones). Cada violacion es un diccionario con
        el ingrediente, la ruta y la clase prohibida, y explica por que
        el plato no cumple.
    """
    prohibidas = onto["categorias"][categoria]["prohibidas"]
    ingredientes = ingredientes_de_plato(plato, carta)

    # PlatoValido exige al menos un ingrediente. Sin esto, un plato vacio
    # cumpliria todas las categorias por "verdad vacia" (∀ sobre nada).
    if len(ingredientes) == 0:
        return False, []

    violaciones = []
    for ingrediente, ruta in ingredientes:
        clases_del_ingrediente = ancestros(ingrediente, onto)
        for clase in prohibidas:
            if clase in clases_del_ingrediente:
                violaciones.append({"ingrediente": ingrediente,
                                    "ruta": ruta,
                                    "clase": clase})

    cumple = len(violaciones) == 0
    return cumple, violaciones


def clasificar(plato, onto, carta):
    """Clasifica un plato en todas las categorias de la ontologia.

    Args:
        plato: Nombre del plato.
        onto: La TBox.
        carta: La ABox.

    Returns:
        Tupla (categorias_que_cumple, motivos). motivos es un diccionario
        categoria -> lista de violaciones, para las que no cumple.
    """
    cumple = []
    motivos = {}
    for categoria in onto["categorias"]:
        ok, violaciones = comprobar_categoria(plato, categoria, onto, carta)
        if ok:
            cumple.append(categoria)
        else:
            motivos[categoria] = violaciones
    return cumple, motivos


# 5. Subsuncion (nivel de concepto: categoria ⊑ categoria)

def prohibidas_cerradas(categoria, onto):
    """Calcula F*(C): los ingredientes atomicos que una categoria no permite.

    Args:
        categoria: Nombre de la categoria.
        onto: La TBox.

    Returns:
        Conjunto de ingredientes atomicos prohibidos.
    """
    prohibidas = onto["categorias"][categoria]["prohibidas"]
    resultado = set()
    for clase in prohibidas:
        resultado = resultado | hojas_bajo(clase, onto)
    return resultado


def subsume(c, d, onto):
    """Comprueba si C ⊑ D, es decir, si todo plato posible de C es tambien de D.

    Subsuncion estructural: se comparan las DEFINICIONES, no los platos
    de la carta. Como toda categoria es "no contiene nada de F(C)":

        C ⊑ D   <=>   F*(D) ⊆ F*(C)

    (si C prohibe todo lo que prohibe D, cualquier plato de C es de D).

    Supuesto (cierre del dominio): los unicos ingredientes posibles son las
    hojas declaradas en la TBox. Por eso la subsuncion es exacta respecto a
    esta ontologia: si se anade un ingrediente nuevo, el resultado puede
    cambiar (se ve en la practica con el Arroz y el experimento de consistencia).

    Args:
        c: Nombre de la categoria C.
        d: Nombre de la categoria D.
        onto: La TBox.

    Returns:
        (True, None) si C ⊑ D, o (False, contraejemplo). El contraejemplo
        es un ingrediente h tal que el plato hipotetico {h} esta en C pero
        no en D.
    """
    prohibidas_c = prohibidas_cerradas(c, onto)
    prohibidas_d = prohibidas_cerradas(d, onto)
    sobrantes = prohibidas_d - prohibidas_c

    if len(sobrantes) == 0:
        return True, None
    return False, sorted(sobrantes)[0]


def jerarquia_categorias(onto):
    """Comprueba la subsuncion para todas las parejas de categorias.

    Args:
        onto: La TBox.

    Returns:
        Lista de diccionarios con las claves c, d, subsume y contraejemplo.
    """
    resultados = []
    for c in onto["categorias"]:
        for d in onto["categorias"]:
            if c != d:
                ok, contraejemplo = subsume(c, d, onto)
                resultados.append({"c": c, "d": d,
                                   "subsume": ok,
                                   "contraejemplo": contraejemplo})
    return resultados


# 6. Consistencia (¿puede existir un plato asi?)

def es_satisfacible(categorias, requiere, onto):
    """Comprueba si puede existir un plato que cumpla un concepto.

    El concepto es: cumplir todas las `categorias` y contener al menos un
    ingrediente de cada clase de `requiere`. Ejemplo:

        Vegetariano ⊓ ∃contiene.Pescado
            -> es_satisfacible(["Vegetariano"], ["Pescado"], onto)

    Args:
        categorias: Categorias que el plato debe cumplir.
        requiere: Clases de las que el plato debe contener algo.
        onto: La TBox.

    Returns:
        (True, plato_testigo) o (False, motivo).
    """
    # Ingredientes prohibidos por alguna de las categorias
    prohibidos = set()
    for categoria in categorias:
        prohibidos = prohibidos | prohibidas_cerradas(categoria, onto)
    permitidos = hojas(onto) - prohibidos

    # PlatoValido: hace falta al menos un ingrediente permitido
    if len(permitidos) == 0:
        return False, "no queda ningun ingrediente permitido"

    testigo = []
    for clase in requiere:
        candidatos = hojas_bajo(clase, onto) & permitidos
        if len(candidatos) == 0:
            return False, (f"todo ingrediente de {clase} esta prohibido por "
                           + " ⊓ ".join(categorias))
        testigo.append(sorted(candidatos)[0])

    if len(testigo) == 0:
        testigo.append(sorted(permitidos)[0])

    return True, testigo


# 7. Auditoria de la carta

def auditar_carta(onto, carta):
    """Compara lo que la carta afirma con lo que infiere el razonador.

    - ETIQUETA FALSA: la carta dice que el plato es de C y no lo es
      (peligroso: p. ej., un celiaco que confia en "sin gluten").
    - OMISION: el plato es de C y la carta no lo dice
      (no es peligroso, pero se pierde informacion util para el cliente).

    Para no repetir informacion, una omision de C no se reporta si el
    plato cumple otra categoria D MAS ESPECIFICA que ya la implica
    (D ⊑ C y no C ⊑ D). Por ejemplo, un plato Vegetariano no necesita
    avisar tambien de que es SinCarne. Aqui se usa la subsuncion para
    razonar sobre la propia carta.

    Args:
        onto: La TBox.
        carta: La ABox.

    Returns:
        Lista de discrepancias. Cada una es un diccionario con las claves
        plato, categoria, tipo y motivo.
    """
    discrepancias = []
    for plato, datos in carta["platos"].items():
        inferidas, motivos = clasificar(plato, onto, carta)
        declaradas = datos["etiquetas_carta"]

        for categoria in declaradas:
            if categoria not in inferidas:
                discrepancias.append({"plato": plato,
                                      "categoria": categoria,
                                      "tipo": "ETIQUETA FALSA",
                                      "motivo": motivos[categoria]})

        for categoria in inferidas:
            if categoria in declaradas:
                continue
            if not implicada_por_otra(categoria, inferidas, onto):
                discrepancias.append({"plato": plato,
                                      "categoria": categoria,
                                      "tipo": "OMISION",
                                      "motivo": []})
    return discrepancias


def implicada_por_otra(categoria, categorias_del_plato, onto):
    """Comprueba si otra categoria del plato, mas especifica, ya implica esta.

    Se exige que sea ESTRICTAMENTE mas especifica: si dos categorias son
    equivalentes (C ⊑ D y D ⊑ C), cada una "implicaria" a la otra y no se
    avisaria de ninguna.

    Args:
        categoria: Categoria que se quiere comprobar.
        categorias_del_plato: Categorias que cumple el plato.
        onto: La TBox.

    Returns:
        True si alguna otra categoria del plato la implica.
    """
    for otra in categorias_del_plato:
        if otra == categoria:
            continue
        otra_implica, _ = subsume(otra, categoria, onto)
        categoria_implica, _ = subsume(categoria, otra, onto)
        if otra_implica and not categoria_implica:
            return True
    return False


# 8. Utilidad para mostrar justificaciones

def texto_violacion(violacion):
    """Convierte una violacion en una frase legible.

    Ejemplo: 'Leche (HeladoDePistacho -> BaseHelado) es ConLactosa'.

    Args:
        violacion: Diccionario con las claves ingrediente, ruta y clase.

    Returns:
        La frase que explica la violacion.
    """
    ruta = " -> ".join(violacion["ruta"])
    return f"{violacion['ingrediente']} ({ruta}) es {violacion['clase']}"
