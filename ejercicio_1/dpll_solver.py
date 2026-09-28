"""
DPLLSolver
----------
Implementa DPLL (Davis-Putnam-Logemann-Loveland), libro 4a ed. figura 7.17.

Idea general del algoritmo, en 4 pasos, en este orden de prioridad:
    1. Si ya no quedan clausulas, TODO se cumple; si alguna clausula se
       ha quedado vacia, ya es imposible cumplirla (terminacion anticipada).
    2. Si hay una clausula con un solo literal, ese valor esta obligado
       -> asignarlo (clausula unitaria).
    3. Si una variable aparece siempre con el mismo signo en las
       clausulas que faltan -> asignarla directamente (simbolo puro).
    4. Si no hay ningun atajo, elegir una variable y probar los dos
       valores posibles. Si uno falla, probar el otro
       (ramificar + retroceder / backtracking).

Cada vez que se asigna un literal, la formula se SIMPLIFICA: se quitan
las clausulas que ya se cumplen y, de las demas, el literal contrario
(que ya es falso). Asi los pasos 1-3 se leen directamente de las
clausulas que quedan, sin recorrer la asignacion:
    clausula vacia        -> conflicto
    clausula de 1 literal -> unitaria
    literal sin su negado -> simbolo puro
En el paso 4 se ramifica por la variable que aparece en mas clausulas:
es la que mas simplifica la formula, sea cual sea el valor que tome.

El solver no sabe nada del dominio del problema (grafos, mapas, etc):
solo trabaja con numeros (variables) y conjuntos de numeros (clausulas).

Para los experimentos, los pasos 2 y 3 se pueden desactivar (ablacion)
y cada llamada a solve() deja sus contadores en self.estadisticas.
"""

import time
from collections import Counter
from dataclasses import dataclass


@dataclass
class Estadisticas:
    llamadas: int = 0  # llamadas recursivas a _dpll
    decisiones: int = 0  # valores probados al ramificar (paso 4)
    propagaciones: int = 0  # asignaciones forzadas por clausula unitaria (paso 2)
    simbolos_puros: int = 0  # asignaciones por simbolo puro (paso 3)
    conflictos: int = 0  # veces que alguna clausula se queda vacia
    retrocesos: int = 0  # valores probados que fallan y obligan a probar otro o volver atras
    tiempo: float = 0.0  # segundos (perf_counter)


def simplificar(clausulas, literal):
    """Formula que queda al hacer 'literal' verdadero."""
    resultado = []
    for clausula in clausulas:
        if literal in clausula:
            continue  # ya se cumple
        if -literal in clausula:
            clausula = clausula - {-literal}  # ese literal ya es falso
        resultado.append(clausula)
    return resultado


class DPLLSolver:

    def __init__(self, usar_unitaria=True, usar_puro=True):
        """
        Args:
            usar_unitaria: Aplicar la regla de la clausula unitaria (paso 2).
            usar_puro: Aplicar la regla del simbolo puro (paso 3).
        Con las dos a False queda el backtracking basico: sigue siendo
        correcto (la ramificacion prueba todo), pero explora mas.
        """
        self.usar_unitaria = usar_unitaria
        self.usar_puro = usar_puro
        self.estadisticas = Estadisticas()

    def solve(self, clauses):
        """Punto de entrada. Devuelve una asignacion (variable -> bool) que
        satisface 'clauses', o None si no existe ninguna (UNSAT). Las
        variables que no hacen falta pueden quedar sin asignar."""
        self.estadisticas = Estadisticas()
        inicio = time.perf_counter()
        resultado = self._dpll([frozenset(c) for c in clauses], {})
        self.estadisticas.tiempo = time.perf_counter() - inicio
        return resultado

    def _dpll(self, clausulas, asignacion):
        self.estadisticas.llamadas += 1

        # paso 1: terminacion anticipada
        if not clausulas:
            return asignacion
        if any(len(c) == 0 for c in clausulas):
            self.estadisticas.conflictos += 1
            return None

        # paso 2: clausula unitaria
        if self.usar_unitaria:
            unitaria = next((c for c in clausulas if len(c) == 1), None)
            if unitaria is not None:
                self.estadisticas.propagaciones += 1
                (literal,) = unitaria
                return self._asignar(clausulas, asignacion, literal)

        # paso 3: simbolo puro
        if self.usar_puro:
            literales = {l for c in clausulas for l in c}
            puro = next((l for l in literales if -l not in literales), None)
            if puro is not None:
                self.estadisticas.simbolos_puros += 1
                return self._asignar(clausulas, asignacion, puro)

        # paso 4: ramificar por la variable mas frecuente
        frecuencia = Counter(abs(l) for c in clausulas for l in c)
        variable = frecuencia.most_common(1)[0][0]
        for literal in (variable, -variable):
            self.estadisticas.decisiones += 1
            resultado = self._asignar(clausulas, asignacion, literal)
            if resultado is not None:
                return resultado
            self.estadisticas.retrocesos += 1

        return None  # las dos ramas fallaron -> conflicto, retroceder

    def _asignar(self, clausulas, asignacion, literal):
        """Hace 'literal' verdadero y sigue con la formula simplificada.
        La asignacion se copia, asi cada rama del arbol tiene la suya."""
        nueva = dict(asignacion)
        nueva[abs(literal)] = literal > 0
        return self._dpll(simplificar(clausulas, literal), nueva)
