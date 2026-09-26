"""
LogicalAgent
------------
El agente basado en conocimiento (KB-Agent, Figura 7.1 de Russell &
Norvig). Sigue el ciclo:

    TELL(KB, percepcion)
    accion <- ASK(KB, ...)

Aplicado a colorear el grafo:
    1. Le pide al Environment que se traduzca a clausulas (el entorno
       sabe hacerlo porque conoce el dominio: regiones, colores, etc)
    2. TELL: anota esas clausulas en su KnowledgeBase
    3. ASK:  le pregunta a la KnowledgeBase si existe una solucion
             (la KnowledgeBase, a su vez, se apoya en el DPLLSolver)
    4. Comprueba el resultado contra el Environment real (goal_test)

Fijate en el paso 1: es el UNICO punto de todo el programa donde se
cruza la frontera entre "el mundo real" (Environment, que sabe de
mapas) y "el razonamiento logico" (KnowledgeBase/DPLLSolver, que solo
saben de clausulas). El agente es quien hace ese cruce.
"""

from knowledge_base import KnowledgeBase
from dpll_solver import DPLLSolver


class LogicalAgent:

    def __init__(self):
        self.kb = KnowledgeBase()
        self.solver = DPLLSolver()

    def tell(self, clauses):
        self.kb.tell_many(clauses) # anota muchas clausulas  (restricciones) a la vez en la BC

    def ask(self):
        return self.kb.ask(self.solver)

    def run(self, environment):
        """Ejecuta un ciclo completo del agente sobre un entorno."""
        clausulas_traducidas = environment.traducir_a_clausulas()
        self.tell(clausulas_traducidas)

        asignacion_encontrada = self.ask()

        if asignacion_encontrada is None:
            return None  # UNSAT: no existe ninguna asignacion valida

        # doble chequeo: la asignacion que dio el solver, funcionatambien vista desde el Environment (el mundo real)?
        if environment.goal_test(asignacion_encontrada):
            return asignacion_encontrada

        return None
