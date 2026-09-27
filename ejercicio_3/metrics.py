"""
metrics.py
----------
Factor de ramificacion efectivo b* (libro 4a ed. seccion 3.6.1, tabla de
la figura 3.26 en las diapositivas): el b que cumple

    N + 1 = 1 + b + b^2 + ... + b^d

con N = nodos GENERADOS y d = profundidad de la solucion. Se despeja por
biseccion.

PASO 3 -- pendiente de implementar.
"""


def factor_ramificacion_efectivo(nodos_generados, profundidad, tolerancia=1e-6):
    raise NotImplementedError
