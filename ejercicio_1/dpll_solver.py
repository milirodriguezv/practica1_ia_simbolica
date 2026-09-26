"""
DPLLSolver
----------
Implementa DPLL (Davis-Putnam-Logemann-Loveland).
Referencia: 02_Apuntes_de_Clase.md, seccion "Busqueda con backtracking
(DPLL)".

Idea general del algoritmo, en 4 pasos, en este orden de prioridad:
    1. Si con la asignacion actual ya se puede saber que TODO se
       cumple, o que YA es imposible cumplirlo -> terminar aqui
       (terminacion anticipada).
    2. Si hay una clausula con un solo literal sin asignar, ese valor
       esta obligado -> asignarlo (clausula unitaria).
    3. Si una variable aparece siempre con el mismo signo en las
       clausulas que faltan -> asignarla directamente (simbolo puro).
    4. Si no hay ningun atajo, elegir una variable libre y probar los
       dos valores posibles. Si uno falla, probar el otro
       (ramificar + retroceder / backtracking).

El solver no sabe nada del dominio del problema (grafos, mapas, etc):
solo trabaja con numeros (variables) y conjuntos de numeros (clausulas).
"""


class DPLLSolver:

    def solve(self, clauses):
        """Punto de entrada. Devuelve una asignacion que satisface
        'clauses', o None si no existe ninguna (UNSAT)."""
        variables = self._obtener_variables(clauses)
        asignacion_inicial = {}
        return self._dpll(clauses, variables, asignacion_inicial)

    # ------------------------------------------------------------
    # El algoritmo principal (recursivo)
    # ------------------------------------------------------------
    def _dpll(self, clauses, variables, assignment):

        estado = self._evaluar_clausulas(clauses, assignment)

        if estado == "SATISFECHA":
            return assignment

        if estado == "CONTRADICCION":
            return None

        # paso 2: clausula unitaria
        forzado = self._buscar_clausula_unitaria(clauses, assignment)
        if forzado is not None:
            variable, valor = forzado
            return self._dpll(clauses, variables, self._con_nueva_asignacion(assignment, variable, valor))

        # paso 3: simbolo puro
        puro = self._buscar_simbolo_puro(clauses, assignment, variables)
        if puro is not None:
            variable, valor = puro
            return self._dpll(clauses, variables, self._con_nueva_asignacion(assignment, variable, valor))

        # paso 4: no hay atajos -> elegir variable y probar los 2 valores
        variable_libre = self._elegir_variable_sin_asignar(variables, assignment)
        if variable_libre is None:
            return None  # no quedan variables y no se resolvio arriba

        for valor in (True, False):
            nueva_asignacion = self._con_nueva_asignacion(assignment, variable_libre, valor)
            resultado = self._dpll(clauses, variables, nueva_asignacion)
            if resultado is not None:
                return resultado

        return None  # las dos ramas fallaron -> conflicto, retroceder

    def _con_nueva_asignacion(self, assignment, variable, valor):
        # devuelve una COPIA de la asignacion con la variable nueva
        # anadida (asi cada rama del arbol tiene su propia copia y no
        # se pisan entre si)
        nueva = dict(assignment)
        nueva[variable] = valor
        return nueva

    # ------------------------------------------------------------
    # Funciones auxiliares. Cada una hace una sola cosa.
    # ------------------------------------------------------------
    def _obtener_variables(self, clauses):
        variables = set()
        for clause in clauses:
            for literal in clause:
                variables.add(abs(literal))
        return variables

    def _valor_del_literal(self, literal, assignment):
        # devuelve True, False, o None si la variable aun no esta asignada
        variable = abs(literal)
        if variable not in assignment:
            return None
        valor_variable = assignment[variable]
        if literal > 0:
            return valor_variable
        return not valor_variable

    def _evaluar_clausulas(self, clauses, assignment):
        """Revisa TODAS las clausulas con la asignacion actual.
        Devuelve "SATISFECHA", "CONTRADICCION" o "INDEFINIDA"."""
        hay_alguna_sin_decidir = False

        for clause in clauses:
            clausula_cumplida = False
            clausula_aun_posible = False

            for literal in clause:
                valor = self._valor_del_literal(literal, assignment)
                if valor is True:
                    clausula_cumplida = True
                if valor is True or valor is None:
                    clausula_aun_posible = True

            if clausula_cumplida:
                continue
            if not clausula_aun_posible:
                return "CONTRADICCION"
            hay_alguna_sin_decidir = True

        if hay_alguna_sin_decidir:
            return "INDEFINIDA"
        return "SATISFECHA"

    def _buscar_clausula_unitaria(self, clauses, assignment):
        for clause in clauses:
            pendientes = []
            clausula_cumplida = False

            for literal in clause:
                valor = self._valor_del_literal(literal, assignment)
                if valor is True:
                    clausula_cumplida = True
                    break
                if valor is None:
                    pendientes.append(literal)

            if clausula_cumplida:
                continue

            if len(pendientes) == 1:
                literal_forzado = pendientes[0]
                variable = abs(literal_forzado)
                valor_forzado = literal_forzado > 0
                return (variable, valor_forzado)

        return None

    def _buscar_simbolo_puro(self, clauses, assignment, variables):
        signos_por_variable = {}

        for clause in clauses:
            clausula_cumplida = False
            for literal in clause:
                if self._valor_del_literal(literal, assignment) is True:
                    clausula_cumplida = True
                    break
            if clausula_cumplida:
                continue  # esta clausula ya no importa para el simbolo puro

            for literal in clause:
                variable = abs(literal)
                if variable in assignment:
                    continue
                signo_positivo = literal > 0
                if variable not in signos_por_variable:
                    signos_por_variable[variable] = set()
                signos_por_variable[variable].add(signo_positivo)

        for variable, signos in signos_por_variable.items():
            if len(signos) == 1:
                unico_signo = list(signos)[0]
                return (variable, unico_signo)

        return None

    def _elegir_variable_sin_asignar(self, variables, assignment):
        for variable in variables:
            if variable not in assignment:
                return variable
        return None
