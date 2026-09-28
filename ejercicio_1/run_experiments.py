"""
run_experiments.py
------------------
Experimentos del ejercicio 1 sobre 3-SAT aleatorio (generadores.py).
Cada uno escribe un CSV en results/ (una fila por formula y configuracion):

    E1  correccion: DPLL da la misma respuesta que la fuerza bruta
    E2  ablacion: decisiones de DPLL con y sin clausula unitaria y
        simbolo puro, al crecer n (en m/n = 4.26, la zona mas dificil)
    E3  transicion de fase: P(SAT) y coste de DPLL frente a m/n, para
        varios n

Semillas fijas: volver a ejecutar da los mismos CSV (salvo el tiempo).
Uso: python run_experiments.py      (~1 min)
"""

import csv
import itertools
from pathlib import Path

from dpll_solver import DPLLSolver
from generadores import cnf_aleatoria

CARPETA_RESULTADOS = Path(__file__).parent / "results"
RAZON_CRITICA = 4.26


def satisfacible_fuerza_bruta(clausulas, n):
    """Prueba las 2^n asignaciones: referencia independiente de DPLL."""
    for valores in itertools.product([False, True], repeat=n):
        if all(any(valores[abs(l) - 1] == (l > 0) for l in c) for c in clausulas):
            return True
    return False


def ejecutar(clausulas, usar_unitaria=True, usar_puro=True):
    solver = DPLLSolver(usar_unitaria, usar_puro)
    sat = solver.solve(clausulas) is not None
    e = solver.estadisticas
    return {"sat": sat, "decisiones": e.decisiones, "propagaciones": e.propagaciones,
            "retrocesos": e.retrocesos, "tiempo": e.tiempo}


def guardar_csv(filas, nombre):
    CARPETA_RESULTADOS.mkdir(exist_ok=True)
    ruta = CARPETA_RESULTADOS / nombre
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=list(filas[0]))
        escritor.writeheader()
        escritor.writerows(filas)
    print(f"  -> results/{nombre} ({len(filas)} filas)")


def e1_correccion(n=10, n_formulas=200):
    """Formulas pequenas (2^10 asignaciones) con m/n entre 2 y 7, para que
    haya tanto SAT como UNSAT."""
    filas = []
    for semilla in range(n_formulas):
        m = round(n * (2 + 5 * semilla / n_formulas))
        clausulas = cnf_aleatoria(n, m, semilla)
        dpll = ejecutar(clausulas)["sat"]
        referencia = satisfacible_fuerza_bruta(clausulas, n)
        filas.append({"n": n, "m": m, "semilla": semilla, "sat_dpll": dpll,
                      "sat_fuerza_bruta": referencia, "coinciden": dpll == referencia})
    guardar_csv(filas, "e1_correccion.csv")
    aciertos = sum(f["coinciden"] for f in filas)
    n_sat = sum(f["sat_fuerza_bruta"] for f in filas)
    print(f"  DPLL = fuerza bruta en {aciertos}/{n_formulas} formulas "
          f"({n_sat} SAT, {n_formulas - n_sat} UNSAT)")


def e2_ablacion(tamanos=range(10, 45, 5), n_formulas=20):
    configuraciones = {"DPLL completo": (True, True), "sin simbolo puro": (True, False),
                       "sin clausula unitaria": (False, True), "backtracking basico": (False, False)}
    filas = []
    for n in tamanos:
        for semilla in range(n_formulas):
            clausulas = cnf_aleatoria(n, round(RAZON_CRITICA * n), semilla)
            for nombre, (unitaria, puro) in configuraciones.items():
                filas.append({"n": n, "semilla": semilla, "configuracion": nombre,
                              **ejecutar(clausulas, unitaria, puro)})
        print(f"  E2 n={n} hecho")
    guardar_csv(filas, "e2_ablacion.csv")


def e3_transicion_de_fase(tamanos=(25, 50, 75), n_formulas=30):
    razones = [2 + 0.25 * i for i in range(21)]  # 2.0, 2.25, ..., 7.0
    filas = []
    for n in tamanos:
        for razon in razones:
            for semilla in range(n_formulas):
                clausulas = cnf_aleatoria(n, round(razon * n), semilla)
                filas.append({"n": n, "razon": razon, "semilla": semilla, **ejecutar(clausulas)})
        print(f"  E3 n={n} hecho")
    guardar_csv(filas, "e3_transicion.csv")


if __name__ == "__main__":
    print("--- E1 correccion ---")
    e1_correccion()
    print("--- E2 ablacion ---")
    e2_ablacion()
    print("--- E3 transicion de fase ---")
    e3_transicion_de_fase()
