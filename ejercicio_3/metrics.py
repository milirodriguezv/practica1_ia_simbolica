"""Factor de ramificacion efectivo b*.

Definido en el libro (4a ed. seccion 3.6.1, tabla de la figura 3.26
en las diapositivas) como el b que cumple

    N + 1 = 1 + b + b^2 + ... + b^d

con N = nodos GENERADOS (sin contar la raiz) y d = profundidad de la
solucion. Es el factor de ramificacion que tendria un arbol uniforme de
profundidad d con N + 1 nodos. Cuanto mas cerca de 1, mejor la heuristica.
Se despeja por biseccion.
"""


def factor_ramificacion_efectivo(nodos_generados, profundidad, tolerancia=1e-6):
    """Despeja b* de N + 1 = 1 + b + ... + b^d por biseccion.

    Args:
        nodos_generados: N, nodos generados sin contar la raiz.
        profundidad: d, numero de pasos de la solucion (d >= 1).
        tolerancia: Anchura del intervalo [lo, hi] a la que se para.

    Returns:
        b* (>= 1), o None si d < 1 (S = G: no hay arbol que medir).

    Example:
        Ejemplo del libro: N = 52, d = 5  ->  b* = 1.92
    """
    N, d = nodos_generados, profundidad
    if d is None or d < 1:
        return None
    if N < d:
        raise ValueError(f"Con profundidad {d} hacen falta al menos {d} nodos generados (hay {N})")

    def nodos_arbol(b):
        """b + b^2 + ... + b^d (sin la raiz)."""
        return sum(b**i for i in range(1, d + 1))

    # En b = 1 el arbol tiene d nodos (<= N) y en b = N^(1/d) tiene al
    # menos b^d = N, asi que la solucion esta en [1, N^(1/d)]. nodos_arbol
    # es creciente en b. (Con hi = N, b^d desborda para d grande.)
    lo, hi = 1.0, N ** (1 / d)
    while hi - lo > tolerancia:
        medio = (lo + hi) / 2
        if nodos_arbol(medio) < N:
            lo = medio
        else:
            hi = medio
    return (lo + hi) / 2


def b_estrella(resultado):
    """Calcula b* a partir del resultado de una busqueda.

    El contador 'generados' del resultado incluye S (la raiz), asi que
    N = generados - 1.

    Args:
        resultado: ResultadoBusqueda de search.py.

    Returns:
        b*, o None si la solucion no tiene ningun paso.
    """
    return factor_ramificacion_efectivo(resultado.generados - 1, resultado.profundidad)
