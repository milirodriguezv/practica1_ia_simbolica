"""
KnowledgeBase
-------------
Es la "libreta" del agente (ver 02_Apuntes_de_Clase.md: "Base de
conocimiento: conjunto de sentencias. Se puede pensar como una libreta
de hechos").

Solo hace dos cosas, como el KB-Agent de la Figura 7.1:
    - TELL:  anota una clausula nueva
    - ASK:   pregunta si, con todo lo anotado, existe una solucion

IMPORTANTE: a diferencia de Environment, la KnowledgeBase NO sabe nada
de "regiones" ni "colores" ni "grafos". Solo entiende clausulas (numeros
y listas de numeros). Es logica pura, sin ningun conocimiento del
dominio concreto del problema.

La KnowledgeBase tampoco sabe resolver el problema por si misma. Cuando
le preguntan (ask), se lo pasa al DPLLSolver, que es quien realmente
razona.
"""


class KnowledgeBase:

    def __init__(self):
        self.clauses = []

    def tell(self, clause):
        """Anota una clausula nueva (una regla que se debe cumplir)."""
        self.clauses.append(clause)

    def tell_many(self, clauses):
        for clause in clauses:
            self.tell(clause)

    def ask(self, solver):
        """
        Pregunta: 'con todo lo que tengo anotado, existe una asignacion
        de valores que lo satisfaga todo?'
        Delega la respuesta en el solver (DPLLSolver).
        """
        return solver.solve(self.clauses)
