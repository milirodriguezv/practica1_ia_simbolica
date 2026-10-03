"""Base de conocimiento (KnowledgeBase) del agente logico.

Es la "libreta" del agente (apuntes de clase: "Base de conocimiento:
conjunto de sentencias. Se puede pensar como una libreta de hechos").

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
    """Conjunto de clausulas con las operaciones TELL y ASK."""

    def __init__(self):
        self.clauses = []

    def tell(self, clause):
        """Anota una clausula nueva (una regla que se debe cumplir).

        Args:
            clause: Clausula (conjunto de enteros).
        """
        self.clauses.append(clause)

    def tell_many(self, clauses):
        """Anota varias clausulas a la vez.

        Args:
            clauses: Lista de clausulas.
        """
        for clause in clauses:
            self.tell(clause)

    def ask(self, solver):
        """Pregunta si existe una asignacion que satisfaga todo lo anotado.

        La respuesta se delega en el solver.

        Args:
            solver: Objeto con un metodo solve(clausulas), p. ej. DPLLSolver.

        Returns:
            La asignacion encontrada (variable -> bool) o None si no existe.
        """
        return solver.solve(self.clauses)
