"""Entorno del ejercicio: el terreno de Marte por el que se mueve el rover.

Es el ENTORNO del ejercicio: el trozo de Marte por el que se mueve el
rover (mismo papel que environment.py en el ejercicio 1).

Contiene dos cosas:

    1. El GENERADOR de terreno sintetico (memoria, "Generacion del
       terreno"). Superpone tres componentes:
           - relieve base: ruido gaussiano suavizado
           - crateres: cuenco parabolico + borde elevado (ecuacion del crater)
           - rocas: discos de celdas intransitables
       Todo depende de una semilla, asi que el mismo (parametros, semilla)
       produce siempre el mismo mapa.

    2. La clase Terreno: la matriz de alturas H, la mascara de rocas y
       las reglas FISICAS de movimiento, es decir, que movimientos son
       factibles (memoria, "Factibilidad de un movimiento"):
           (i)   la vecina esta dentro de la cuadricula
           (ii)  la vecina no es roca
           (iii) |pendiente del movimiento| <= THETA_MAX
           (iv)  en diagonal, ninguna de las dos celdas de la esquina es roca

El terreno NO sabe nada de costes, heuristicas ni algoritmos de
busqueda: eso es cosa de problem.py, heuristics.py y search.py. Aqui
solo esta "el mundo".
"""

import math
from collections import deque
from dataclasses import asdict, dataclass

import numpy as np
from parametros import DIRECCIONES, S_CELL, THETA_MAX
from scipy.ndimage import gaussian_filter


@dataclass
class ParametrosGenerador:
    """Controles de dificultad del generador de terreno.

    Las distancias van en metros salvo que se indique "celdas".
    """

    N: int = 200  # tamano de la cuadricula N x N
    sigma_base: float = 10.0  # suavizado del relieve base [celdas]
    amplitud_base: float = 1.0  # altura maxima del relieve base [m]
    n_crateres: int = 12
    radio_min: float = 4.0  # radio de los crateres [m]
    radio_max: float = 20.0
    rho_min: float = 0.10  # profundidad / diametro
    rho_max: float = 0.20
    eta: float = 0.2  # altura del borde, relativa a la profundidad
    w: float = 0.3  # anchura del borde, relativa al radio
    densidad_rocas: float = 0.004  # n_rocas = densidad * N^2
    radio_roca_min: int = 1  # radio de cada roca [celdas], ya con margen
    radio_roca_max: int = 2
    separacion_min: float = 0.7  # |S - G| >= separacion_min * N * s
    max_intentos: int = 50  # instancias a probar antes de rendirse


# ---------------------------------------------------------------------
#  Componentes del generador (funciones puras: rng + parametros -> array)
# ---------------------------------------------------------------------


def generar_relieve_base(rng, N, sigma, amplitud):
    """Genera el relieve base: ondulaciones suaves del orden de metros.

    Es ruido blanco gaussiano suavizado con un filtro gaussiano y
    reescalado para que su altura maxima (en valor absoluto) sea amplitud.

    Args:
        rng: Generador aleatorio de numpy.
        N: Tamano del mapa (N x N).
        sigma: Suavizado del filtro, en celdas.
        amplitud: Altura maxima del relieve, en metros.

    Returns:
        Matriz N x N de alturas.
    """
    ruido = rng.normal(size=(N, N))
    base = gaussian_filter(ruido, sigma=sigma, mode="reflect")
    base -= base.mean()
    return base * (amplitud / np.abs(base).max())


def altura_crater(r, radio, profundidad, eta, w):
    """Calcula el perfil de un crater segun la distancia a su centro.

        h(r) = -D * max(0, 1 - r^2/R^2)  +  eta * D * exp(-((r - R) / (w R))^2)
               (cuenco)                     (borde elevado)

    Args:
        r: Distancia (o matriz de distancias) al centro, en metros.
        radio: Radio R del crater.
        profundidad: Profundidad D del cuenco.
        eta: Altura del borde, relativa a la profundidad.
        w: Anchura del borde, relativa al radio.

    Returns:
        Altura en cada distancia r.
    """
    cuenco = -profundidad * np.maximum(0.0, 1.0 - r**2 / radio**2)
    borde = eta * profundidad * np.exp(-(((r - radio) / (w * radio)) ** 2))
    return cuenco + borde


def generar_crateres(rng, N, s, p):
    """Suma crateres de centro, radio y profundidad aleatorios.

    Args:
        rng: Generador aleatorio de numpy.
        N: Tamano del mapa (N x N).
        s: Lado de cada celda, en metros.
        p: ParametrosGenerador.

    Returns:
        Matriz N x N con la altura que aportan los crateres.
    """
    filas, columnas = np.indices((N, N))
    alturas = np.zeros((N, N))

    for _ in range(p.n_crateres):
        ci, cj = rng.uniform(0, N, size=2)
        radio = rng.uniform(p.radio_min, p.radio_max)
        rho = rng.uniform(p.rho_min, p.rho_max)
        profundidad = rho * 2 * radio

        # La distancia r a cada celda, en metros, desde el centro del crater.
        r = s * np.hypot(filas - ci, columnas - cj)
        alturas += altura_crater(r, radio, profundidad, p.eta, p.w)

    return alturas


def generar_rocas(rng, N, p):
    """Coloca rocas: discos de celdas intransitables.

    Args:
        rng: Generador aleatorio de numpy.
        N: Tamano del mapa (N x N).
        p: ParametrosGenerador.

    Returns:
        Matriz booleana N x N, True donde hay roca.
    """
    filas, columnas = np.indices((N, N))
    rocas = np.zeros((N, N), dtype=bool)
    n_rocas = round(p.densidad_rocas * N * N)

    for _ in range(n_rocas):
        ci, cj = rng.integers(0, N, size=2)
        radio = rng.integers(p.radio_roca_min, p.radio_roca_max + 1)
        rocas |= (filas - ci) ** 2 + (columnas - cj) ** 2 <= radio**2

    return rocas


# ---------------------------------------------------------------------
#  El entorno
# ---------------------------------------------------------------------


class Terreno:
    """Matriz de alturas, mascara de rocas y reglas fisicas de movimiento."""
    def __init__(
        self,
        alturas,
        rocas,
        s=S_CELL,
        theta_max=THETA_MAX,
        inicio=None,
        objetivo=None,
        semilla=None,
    ):
        """Crea el terreno.

        Args:
            alturas: Matriz de alturas, en metros.
            rocas: Matriz booleana, True donde hay roca.
            s: Lado de cada celda, en metros.
            theta_max: Pendiente maxima permitida, en radianes.
            inicio: Celda (i, j) de partida.
            objetivo: Celda (i, j) de llegada.
            semilla: Semilla con la que se genero (solo informativa).
        """
        self.alturas = np.asarray(alturas, dtype=float)
        self.rocas = np.asarray(rocas, dtype=bool)
        self.s = s
        self.theta_max = theta_max
        self.inicio = inicio
        self.objetivo = objetivo
        self.semilla = semilla

    @property
    def N(self):
        """Tamano del mapa (numero de filas)."""
        return self.alturas.shape[0]

    def dentro(self, celda):
        """Indica si una celda esta dentro de la cuadricula.

        Args:
            celda: Celda (i, j).

        Returns:
            True si esta dentro del mapa.
        """
        i, j = celda
        filas, columnas = self.alturas.shape
        return 0 <= i < filas and 0 <= j < columnas

    def es_transitable(self, celda):
        """Indica si el rover puede estar en una celda.

        Args:
            celda: Celda (i, j).

        Returns:
            True si esta dentro del mapa y no es roca.
        """
        return self.dentro(celda) and not self.rocas[celda]

    def distancia_horizontal(self, di, dj):
        """Distancia horizontal de un movimiento.

        Args:
            di: Desplazamiento en filas.
            dj: Desplazamiento en columnas.

        Returns:
            s en ortogonal o s * sqrt(2) en diagonal.
        """
        return self.s * math.hypot(di, dj)

    def pendiente(self, a, b):
        """Pendiente con signo del movimiento a -> b.

        Args:
            a: Celda de origen (i, j).
            b: Celda de destino (i, j).

        Returns:
            Pendiente en radianes: positiva en subida, negativa en bajada.
        """
        di, dj = b[0] - a[0], b[1] - a[1]
        desnivel = self.alturas[b] - self.alturas[a]
        return math.atan(desnivel / self.distancia_horizontal(di, dj))

    def movimientos_factibles(self, celda):
        """Movimientos que el rover puede hacer desde una celda (reglas i-iv).

        Es lo que usa RoverProblem.actions().

        Args:
            celda: Celda (i, j).

        Returns:
            Lista de desplazamientos (di, dj) factibles.
        """
        if not self.es_transitable(celda):
            return []

        i, j = celda
        factibles = []
        for di, dj in DIRECCIONES:
            vecina = (i + di, j + dj)
            if not self.es_transitable(vecina):  # (i) y (ii)
                continue
            if abs(self.pendiente(celda, vecina)) > self.theta_max:  # (iii)
                continue
            if di != 0 and dj != 0 and (self.rocas[i + di, j] or self.rocas[i, j + dj]):  # (iv)
                continue
            factibles.append((di, dj))
        return factibles

    def es_movimiento_factible(self, celda, di, dj):
        """Indica si un movimiento concreto es factible.

        Args:
            celda: Celda de origen (i, j).
            di: Desplazamiento en filas.
            dj: Desplazamiento en columnas.

        Returns:
            True si el movimiento cumple las reglas i-iv.
        """
        return (di, dj) in self.movimientos_factibles(celda)

    def vecinos_factibles(self, celda):
        """Celdas a las que se puede pasar desde una celda.

        Args:
            celda: Celda (i, j).

        Returns:
            Lista de celdas vecinas alcanzables en un paso.
        """
        i, j = celda
        return [(i + di, j + dj) for di, dj in self.movimientos_factibles(celda)]

    def alcanzables_desde(self, origen):
        """Calcula las celdas a las que se puede llegar desde un origen.

        Usa busqueda en anchura. Como la factibilidad es simetrica
        (|theta(a,b)| = |theta(b,a)|), "b alcanzable desde a" equivale a
        "a alcanzable desde b". Solo se usa para validar instancias: aqui no
        importa el coste, solo si existe camino.

        Args:
            origen: Celda (i, j) de partida.

        Returns:
            Matriz booleana con True en las celdas alcanzables.
        """
        visitado = np.zeros(self.alturas.shape, dtype=bool)
        if not self.es_transitable(origen):
            return visitado

        visitado[origen] = True
        cola = deque([origen])
        while cola:
            celda = cola.popleft()
            for vecina in self.vecinos_factibles(celda):
                if not visitado[vecina]:
                    visitado[vecina] = True
                    cola.append(vecina)
        return visitado

    def mascara_pendiente_excesiva(self):
        """Marca las celdas desde las que algun paso supera THETA_MAX.

        No tiene en cuenta las rocas. Solo se usa para dibujar las paredes de
        los crateres.

        Returns:
            Matriz booleana con True en esas celdas.
        """
        excesiva = np.zeros(self.alturas.shape, dtype=bool)
        for celda in np.ndindex(self.alturas.shape):
            i, j = celda
            excesiva[celda] = any(
                self.dentro((i + di, j + dj))
                and abs(self.pendiente(celda, (i + di, j + dj))) > self.theta_max
                for di, dj in DIRECCIONES
            )
        return excesiva

    def resumen(self):
        """Devuelve una linea de texto con los datos principales del terreno."""
        n_celdas = self.N * self.N
        return (
            f"Terreno {self.N}x{self.N} (s = {self.s} m, semilla = {self.semilla}) | "
            f"alturas [{self.alturas.min():.1f}, {self.alturas.max():.1f}] m | "
            f"rocas {self.rocas.sum() / n_celdas:.1%} | "
            f"S = {self.inicio}, G = {self.objetivo}"
        )


# ---------------------------------------------------------------------
#  Instancias completas: terreno + S + G
# ---------------------------------------------------------------------


def elegir_inicio_objetivo(terreno, rng, separacion_min, intentos=20):
    """Elige S y G validos para un terreno.

    S y G son transitables, estan separados al menos
    separacion_min * N * s y G es alcanzable desde S.

    Args:
        terreno: Terreno ya generado.
        rng: Generador aleatorio de numpy.
        separacion_min: Separacion minima, como fraccion del lado del mapa.
        intentos: Numero de inicios que se prueban.

    Returns:
        Tupla (S, G), o None si no lo consigue.
    """
    distancia_min = separacion_min * terreno.N * terreno.s
    transitables = np.argwhere(~terreno.rocas)
    if len(transitables) == 0:
        return None
    filas, columnas = np.indices((terreno.N, terreno.N))

    for _ in range(intentos):
        inicio = tuple(int(x) for x in transitables[rng.integers(len(transitables))])
        alcanzable = terreno.alcanzables_desde(inicio)
        lejos = (
            terreno.s * np.hypot(filas - inicio[0], columnas - inicio[1])
            >= distancia_min
        )
        candidatos = np.argwhere(alcanzable & lejos)
        if len(candidatos) > 0:
            objetivo = tuple(int(x) for x in candidatos[rng.integers(len(candidatos))])
            return inicio, objetivo

    return None


def generar_terreno(params=None, semilla=0):
    """Genera una instancia completa y reproducible: terreno, S y G.

    Si no hay un par (S, G) valido, regenera el mapa con el mismo generador
    aleatorio, asi que el resultado sigue dependiendo solo de la semilla.

    Args:
        params: ParametrosGenerador. Si es None se usan los de por defecto.
        semilla: Semilla del generador aleatorio.

    Returns:
        Terreno con inicio y objetivo.

    Raises:
        RuntimeError: Si no se encuentra una instancia valida.
    """
    p = params or ParametrosGenerador()
    rng = np.random.default_rng(semilla)

    for _ in range(p.max_intentos):
        base = generar_relieve_base(rng, p.N, p.sigma_base, p.amplitud_base)
        crateres = generar_crateres(rng, p.N, S_CELL, p)
        rocas = generar_rocas(rng, p.N, p)

        terreno = Terreno(base + crateres, rocas, semilla=semilla)
        extremos = elegir_inicio_objetivo(terreno, rng, p.separacion_min)
        if extremos is not None:
            terreno.inicio, terreno.objetivo = extremos
            return terreno

    raise RuntimeError(
        f"No se encontro una instancia valida en {p.max_intentos} intentos "
        f"(semilla {semilla}); prueba menos rocas o crateres mas someros."
    )


# ---------------------------------------------------------------------
#  Guardar / cargar (maps/*.npz) para que los experimentos sean reproducibles
# ---------------------------------------------------------------------


def guardar_terreno(terreno, ruta, params=None):
    """Guarda un terreno en un archivo .npz.

    Args:
        terreno: Terreno a guardar.
        ruta: Ruta del archivo.
        params: ParametrosGenerador con los que se genero (opcional).
    """
    extra = {f"param_{k}": v for k, v in asdict(params).items()} if params else {}
    np.savez_compressed(
        ruta,
        alturas=terreno.alturas,
        rocas=terreno.rocas,
        s=terreno.s,
        theta_max=terreno.theta_max,
        inicio=np.array(terreno.inicio),
        objetivo=np.array(terreno.objetivo),
        semilla=-1 if terreno.semilla is None else terreno.semilla,
        **extra,
    )


def cargar_terreno(ruta):
    """Carga un terreno guardado con guardar_terreno.

    Args:
        ruta: Ruta del archivo .npz.

    Returns:
        El Terreno guardado.
    """
    datos = np.load(ruta)
    semilla = int(datos["semilla"])
    return Terreno(
        datos["alturas"],
        datos["rocas"],
        s=float(datos["s"]),
        theta_max=float(datos["theta_max"]),
        inicio=tuple(int(x) for x in datos["inicio"]),
        objetivo=tuple(int(x) for x in datos["objetivo"]),
        semilla=None if semilla == -1 else semilla,
    )
