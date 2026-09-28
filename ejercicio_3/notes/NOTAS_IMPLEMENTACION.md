# Notas de implementación — Ejercicio 3 (rover en Marte con A*)

Cuaderno de apuntes: qué hace cada parte del código, por qué, y de dónde
sale cada idea. Ir añadiendo a medida que se implementan los pasos.

---

## Índice

1. [Estructura del ejercicio](#1-estructura-del-ejercicio)
2. [parametros.py](#2-parametrospy)
3. [terrain.py — el entorno](#3-terrainpy--el-entorno)
   - 3.1 [Relieve base (ruido + filtro gaussiano)](#31-relieve-base-ruido--filtro-gaussiano)
   - 3.2 [Cráteres](#32-cráteres)
   - 3.3 [Rocas](#33-rocas)
   - 3.4 [Factibilidad de los movimientos](#34-factibilidad-de-los-movimientos)
   - 3.5 [Elegir S y G y comprobar que hay camino](#35-elegir-s-y-g-y-comprobar-que-hay-camino)
   - 3.6 [Guardar y cargar mapas](#36-guardar-y-cargar-mapas)
4. [problem.py — el problema de búsqueda y el coste](#4-problempy--el-problema-de-búsqueda-y-el-coste)
   - 4.1 [La interfaz del problema](#41-la-interfaz-del-problema)
   - 4.2 [`velocidad(theta)`](#42-velocidadtheta)
   - 4.3 [`action_cost` — el coste de un paso](#43-action_cost--el-coste-de-un-paso)
5. [heuristics.py — las estimaciones](#5-heuristicspy--las-estimaciones)
   - 5.1 [h0, h1 y h2](#51-h0-h1-y-h2)
   - 5.2 [Por qué funcionan (admisibles, consistentes, h2 ≥ h1)](#52-por-qué-funcionan-admisibles-consistentes-h2--h1)
   - 5.3 [`ponderada(h, w)`](#53-ponderadah-w)
   - 5.4 [Tests del paso 2](#54-tests-del-paso-2)
6. [Pasos pendientes](#6-pasos-pendientes)
7. [Referencias](#7-referencias)

---

## 1. Estructura del ejercicio

Misma filosofía que el ejercicio 1: **un archivo por concepto**.

| Ejercicio 1 | Ejercicio 3 | Papel |
|---|---|---|
| `environment.py` | `terrain.py` | El mundo (entorno) |
| `logical_agent.py` | `rover_agent.py` | El agente |
| `dpll_solver.py` | `search.py` | El algoritmo |
| `visualizar_mapa.py` | `visualizar_terreno.py` | Dibujar (sin lógica) |
| `main.py` | `main.py` | Lo junta todo |

El terreno **no sabe nada** de costes ni de búsqueda. Solo sabe qué alturas
hay, dónde hay rocas y qué movimientos son físicamente posibles.

---

## 2. parametros.py

Constantes físicas en un solo sitio (las usan `terrain.py`, `problem.py` y
`heuristics.py`). Valores y justificación: Tabla 1 del `.tex`.

| Constante | Valor | De dónde sale |
|---|---|---|
| `S_CELL` | 1 m | Resolución de los DTM de HiRISE |
| `V_MAX` | 0,042 m/s | Velocidad máx. de Perseverance/Curiosity (~150 m/h) |
| `THETA_MAX` | 25° | Margen bajo el límite de 30° de Curiosity |
| `K_SUB`, `K_BAJ` | 0,8 / 0,4 | Pérdida de velocidad en subida / bajada |
| `DIRECCIONES` | 8 pares `(di, dj)` | 8-conectividad |

---

## 3. terrain.py — el entorno

El mapa final es la **suma de capas**:

```
H = relieve base  +  cráteres        (y las rocas van en una máscara aparte)
```

Todo sale de un único generador aleatorio `rng = np.random.default_rng(semilla)`:
**misma semilla → mismo mapa**, que es lo que hace los experimentos reproducibles.

### 3.1 Relieve base (ruido + filtro gaussiano)

**Propósito:** el suelo "normal" de Marte no es plano, tiene lomas suaves.
Esta capa crea esas ondulaciones (la base de la tarta sobre la que luego van
los cráteres y las rocas).

```python
ruido = rng.normal(size=(N, N))                            # 1
base = gaussian_filter(ruido, sigma=sigma, mode="reflect") # 2
base -= base.mean()                                        # 3
return base * (amplitud / np.abs(base).max())              # 4
```

1. **Ruido blanco:** un número aleatorio (normal, media 0, desv. 1) por
   celda. Cada celda es independiente de sus vecinas, así que queda un suelo
   de "pinchos" (`/\/\/\/\`), imposible de recorrer.
2. **Filtro gaussiano (suavizado):** cada celda pasa a ser una **media
   ponderada de sus vecinas**, en la que las cercanas pesan más y las lejanas
   menos (los pesos siguen una campana de Gauss). Es "pasar la mano por la
   arena": los pinchos se convierten en lomas (`~~~~`).
   - `sigma` (10 celdas) = cuánto se alisa ≈ anchura típica de una loma.
     Pequeño → rugoso; grande → lomas amplias.
   - `mode="reflect"`: en los bordes faltan vecinas; se inventan
     reflejando el mapa como en un espejo.
   - Ejemplo 1D con una media simple de 3 vecinas:
     `3, -2, 4, -3, 1` → la celda central queda en `(-2+4-3)/3 ≈ -0,3`.
3. **Centrar en 0:** se resta la media para que el suelo oscile alrededor de 0 m.
4. **Escalar:** tras suavizar, los valores quedan diminutos (~0,03) y no se
   sabe su tamaño exacto. Se dividen por el valor más extremo y se multiplican
   por `amplitud` (1 m), así que todo queda en **[-1, 1] m**.

**Por qué 1 m y sigma = 10:** con lomas de ±1 m repartidas en decenas de metros
la pendiente es de pocos grados. El suelo se puede recorrer, pero sube y baja
(y eso ya tiene coste por la asimetría). Lo que está prohibido viene de los cráteres y las rocas.

**Frase para la memoria:** *"ruido blanco gaussiano suavizado con un filtro
gaussiano de desviación σ_b y reescalado a amplitud A_b"*.

**Idea de fondo:** suavizar ruido blanco con un filtro paso bajo es la forma
más sencilla de generar un *campo aleatorio correlacionado* (las celdas
cercanas tienen alturas parecidas). Es de la misma familia que el ruido de
Perlin o el ruido fractal que se usan en videojuegos para generar terreno,
pero más simple. Ver referencias [R1]–[R5].

### 3.2 Cráteres

**Propósito:** es la segunda capa de la tarta: sobre el suelo ondulado se
**excavan agujeros redondos**. Son los obstáculos "interesantes":

- cráteres **profundos**: paredes de más de 25°, así que **no se pueden cruzar**;
- cráteres **someros**: se pueden cruzar, pero **cuesta tiempo** bajar y subir.

Así el rover tiene que decidir: ¿rodeo el cráter o lo atravieso?

El trabajo se reparte entre dos funciones:

| Función | Qué decide |
|---|---|
| `generar_crateres` | **Dónde** va cada cráter y **de qué tamaño** es |
| `altura_crater` | **Qué forma** tiene (cuánto hundir o levantar cada celda) |

#### 3.2.1 `generar_crateres(rng, N, s, p)`

```python
filas, columnas = np.indices((N, N))           # 1. fila y columna de cada celda
alturas = np.zeros((N, N))                     #    mapa vacío donde se acumulan los cráteres
crateres = []

for _ in range(p.n_crateres):                  # 2. una vuelta por cráter (12)
    ci, cj = rng.uniform(0, N, size=2)         # 3. dados: centro,
    radio = rng.uniform(p.radio_min, p.radio_max)   #  radio (4-20 m),
    rho = rng.uniform(p.rho_min, p.rho_max)         #  profundidad/diámetro (0,10-0,20)
    profundidad = rho * 2 * radio

    r = s * np.hypot(filas - ci, columnas - cj)     # 4. distancia de TODAS las celdas al centro
    alturas += altura_crater(r, radio, profundidad, p.eta, p.w)  # 5. forma del cráter, sumada
    crateres.append({...})                     # 6. apuntar sus datos (solo para consultar)

return alturas, crateres
```

1. **`np.indices`** crea dos matrices con la fila y la columna de cada celda
   (en 3×3: `filas = [[0,0,0],[1,1,1],[2,2,2]]`, `columnas = [[0,1,2],[0,1,2],[0,1,2]]`).
   Sirve para calcular distancias de **todas las celdas a la vez**, sin bucles.
2. Se repite una vez por cráter.
3. **Dados:**
   - **Centro** al azar en el mapa (puede tener decimales, como `(37.4, 81.9)`).
   - **Radio** al azar entre 4 y 20 m.
   - **`rho`** = profundidad ÷ diámetro. En cráteres simples reales vale 0,1–0,2
     (refs. del `.tex`: Krüger 2018, Stopar 2017).
   - **Profundidad** `D = rho · 2R`. Ejemplo: R = 10 m, rho = 0,15, así que D = 3 m.
     Se usa `rho` para que la profundidad sea **proporcional al tamaño**, como
     en la realidad.
4. **`np.hypot(a, b) = √(a² + b²)`** (Pitágoras): metros de cada celda al centro.
   Con el centro en `(1, 1)` de un 3×3:
   ```
   1.41  1.00  1.41
   1.00  0.00  1.00
   1.41  1.00  1.41
   ```
5. `altura_crater` convierte distancia en altura (ver 3.2.2). El **`+=`
   suma** el cráter al mapa: si dos se solapan, sus alturas se suman y aparecen
   cráteres "mordiendo" a otros, como en Marte.
6. La lista `crateres` no afecta al mapa; solo guarda los datos para dibujar o
   describir en la memoria.

Después, fuera de esta función: `H = relieve base + cráteres`.

#### 3.2.2 `altura_crater(r, radio, profundidad, eta, w)`

Responde a: *"si estoy a `r` metros del centro, ¿cuánto bajo o subo el suelo?"*
Un número negativo es hundir, uno positivo es levantar y 0 es no tocar.

```
h(r) = -D·max(0, 1 - r²/R²)   +   η·D·exp(-((r - R)/(w·R))²)
       └─── el agujero ───┘       └──── el borde levantado ───┘
```

| Parámetro | Qué es | Ejemplo |
|---|---|---|
| `r` | Distancia al centro de **todas las celdas** (matriz) | 0, 5, 10… m |
| `radio` (R) | Tamaño del cráter | 10 m |
| `profundidad` (D) | Hondura en el centro | 3 m |
| `eta` (η) | Altura del borde, como fracción de D | 0,2, es decir, 0,6 m |
| `w` | Anchura del borde, como fracción de R | 0,3, es decir, ~3 m |

**Línea 1: el agujero (cuenco parabólico)**
```python
cuenco = -profundidad * np.maximum(0.0, 1.0 - r**2 / radio**2)
```
1. `r²/R²`: vale 0 en el centro, 1 en el borde y más de 1 fuera.
2. `1 - …`: se invierte y queda 1 en el centro, 0 en el borde y **negativo** fuera.
3. `np.maximum(0, …)`: lo negativo pasa a 0, así que **fuera del cráter no se excava**.
   Se usa `np.maximum` (no `max`) porque compara **celda a celda** en la matriz.
4. `-D · …`: se pasa a metros y se pone signo menos (hundir).

Por el `r²`, la forma es una **parábola**: plana en el fondo y cada vez más
empinada hacia el borde.

**Línea 2: el borde levantado (campana de Gauss)**
```python
borde = eta * profundidad * np.exp(-(((r - radio) / (w * radio)) ** 2))
```
1. `r - R`: distancia **al borde** (0 justo en el borde).
2. `/ (w·R)`: medida en "anchuras de borde", así que un cráter grande tiene un borde ancho.
3. `exp(-x²)`: campana, con 1 en el centro y cayendo rápido a los lados:
   ```
   x:        -2    -1     0     1     2
   exp(-x²): 0.02  0.37  1.00  0.37  0.02
   ```
   Queda un **anillo con el pico justo en r = R**.
4. `η·D · …`: el pico mide `η·D`. Más hondo implica más borde (más tierra
   expulsada en el impacto).

**Línea 3:** `return cuenco + borde`.

**Ejemplo con números** (R = 10 m, D = 3 m, η = 0,2, w = 0,3):

| Distancia `r` | Cuenco | Borde | **Total** | Dónde estás |
|---|---|---|---|---|
| 0 m | -3,00 | 0,00 | **-3,00** | Fondo del cráter |
| 5 m | -2,25 | 0,04 | **-2,21** | Bajando por la pared |
| 8 m | -1,08 | 0,38 | **-0,70** | Pared, cerca del borde |
| 10 m | 0,00 | 0,60 | **+0,60** | Cresta del borde |
| 12 m | 0,00 | 0,38 | **+0,38** | Bajando por fuera |
| 15 m | 0,00 | 0,04 | **+0,04** | Casi en el suelo normal |
| 20 m | 0,00 | 0,00 | **0,00** | Fuera, no se toca |

Cómo se calcula, por ejemplo, la fila `r = 8`:
- cuenco = `-3 · max(0, 1 - 64/100)` = `-3 · 0,36` = **-1,08**
- borde = `0,2 · 3 · exp(-((8 - 10)/3)²)` = `0,6 · exp(-0,444)` = `0,6 · 0,641` = **0,38**
- total = -1,08 + 0,38 = **-0,70**

Perfil (el panel 3 de la figura de ejemplo):
```
 +0.6         ╭─╮                 ╭─╮
  0.0  ───────╯  \               /  ╰───────
                  \             /
 -1.5              \           /
                    \         /
 -3.0                 ‾‾‾‾‾‾‾
       r=20  r=10   r=5  r=0  r=5   r=10  r=20
```

#### 3.2.3 Por qué esta fórmula

- **Sencilla:** dos piezas, cada una fácil de explicar en la memoria.
- **Pendiente calculable:** la derivada del cuenco en el borde es
  `2D/R = 4ρ`, así que la pared tiene **`arctan(4ρ)` = entre 21,8° y 38,7°**. Como
  θ_max = 25°, **en cada mapa hay cráteres cruzables y no cruzables**. El
  borde levantado añade algo más de pendiente junto a la cresta, así que las
  paredes reales son algo más empinadas que eso. Comprobado en
  `test_pared_del_crater_es_arctan_4_rho` (con η = 0 para aislar el cuenco).
- **Todo proporcional** (borde ∝ D, anchura ∝ R): un cráter grande es uno pequeño
  ampliado.
- **Vectorizada:** como `r` es la matriz de distancias, 2 líneas calculan la
  altura de todo el mapa sin bucles.

**Resumen:** *para cada cráter se tiran dados (dónde, tamaño, profundidad), se
calcula la distancia de cada celda al centro y se convierte en "cuánto hundir"
con cuenco parabólico + borde gaussiano, y se suma al mapa.*

### 3.3 Rocas

**Propósito:** es la tercera capa de la tarta, las "pepitas de chocolate".
Son celdas por las que el rover **no puede pasar nunca**, sin importar la pendiente.

A diferencia de los cráteres, las rocas **no cambian la altura**. Se guardan en
un mapa aparte de sí/no (**máscara booleana**): `True` = roca, `False` = libre.

#### 3.3.1 `generar_rocas(rng, N, p)`

```python
filas, columnas = np.indices((N, N))                 # 1. fila y columna de cada celda
rocas = np.zeros((N, N), dtype=bool)                 #    mapa todo a False (sin rocas)
n_rocas = round(p.densidad_rocas * N * N)            # 2. cuántas rocas

for _ in range(n_rocas):
    ci, cj = rng.integers(0, N, size=2)              # 3. centro: una celda al azar
    radio = rng.integers(p.radio_roca_min, p.radio_roca_max + 1)   # radio: 1 o 2
    rocas |= (filas - ci) ** 2 + (columnas - cj) ** 2 <= radio**2  # 4. pintar el disco

return rocas
```

1. **Preparar:** `np.indices` como en los cráteres, y un mapa todo a `False`.
2. **Cuántas rocas:** `densidad_rocas = 0,004`, es decir, 4 rocas por cada 1000 celdas:
   - N = 100: 10 000 celdas, **40 rocas**;
   - N = 200: 40 000 celdas, **160 rocas**.

   Se multiplica por `N²` para que todos los tamaños tengan **la misma
   densidad**, así que en E5 la dificultad por m² es la misma.
3. **Dados:**
   - **Centro** con `integers` (no `uniform` como en los cráteres): la roca se
     centra **en una celda concreta**.
   - **Radio** 1 o 2. El `+ 1` hace falta porque en `integers(1, 3)` el límite de arriba
     **no se incluye**, así que da 1 o 2.
4. **Pintar el disco**, en dos partes:
   - **`(filas - ci)² + (columnas - cj)² <= radio²`**: *"¿esta celda está a
     distancia ≤ radio del centro?"*, para todas a la vez. Es Pitágoras sin la
     raíz: `d² ≤ radio²` equivale a `d ≤ radio`, pero es más rápido y con enteros.
     Da una matriz `True`/`False` con forma de disco:
     ```
     radio = 1 (5 celdas)        radio = 2 (13 celdas)
                                  . . █ . .
       . █ .                      . █ █ █ .
       █ █ █                      █ █ █ █ █
       . █ .                      . █ █ █ .
                                  . . █ . .
     ```
     Por eso **en los mapas las rocas se ven como cruces o rombos negros**: un
     "círculo" de 1–2 celdas en una cuadrícula tiene esa forma.
   - **`rocas |= …`**: `|` es un **O lógico** celda a celda: *"hay roca si ya
     la había O si la nueva la cubre"*. Es como pintar con rotulador: lo pintado sigue
     pintado y se añade lo nuevo. Si dos rocas se solapan, se juntan en una
     mancha más grande.

**Ejemplo con números** (roca con centro `(2, 2)` y radio 1, en un 5×5):

| Celda | `(i-2)² + (j-2)²` | ≤ 1 | ¿Roca? |
|---|---|---|---|
| (2, 2) | 0 + 0 = 0 | sí | █ |
| (1, 2) | 1 + 0 = 1 | sí | █ |
| (2, 3) | 0 + 1 = 1 | sí | █ |
| (1, 1) | 1 + 1 = 2 | no | . (la diagonal queda fuera) |
| (0, 2) | 4 + 0 = 4 | no | . |

#### 3.3.2 Detalles

- **¿Por qué discos de 1–2 celdas y no celdas sueltas?** El rover se trata
  como **un punto**, pero mide unos 3 m. Para compensarlo, cada roca se
  "engorda" con medio ancho del rover: si el punto no toca la roca engordada,
  el rover real no toca la roca real. En la memoria: **obstáculo dilatado en
  el espacio de configuraciones** (Russell & Norvig).
- **Las rocas pueden caer en cualquier sitio**, también dentro de cráteres o sobre otra roca.
- **Nunca caen sobre S o G**, porque S y G se eligen **después**, y solo entre
  celdas sin roca (sección 3.5).

**Resumen:** *se calcula cuántas rocas tocan según el tamaño del mapa y, para
cada una, se elige una celda y un radio al azar y se marcan como prohibidas
todas las celdas a esa distancia o menos.*

### 3.4 Factibilidad de los movimientos

Un paso `a → b` (b vecina de a) es factible si:

| Regla | Qué comprueba |
|---|---|
| (i) | `b` está dentro del mapa |
| (ii) | `b` no es roca (ni `a`) |
| (iii) | `|θ(a,b)| ≤ 25°`, con `θ = atan(Δh / d_h)` y `d_h = s` o `s·√2` |
| (iv) | En diagonal, las 2 celdas de la esquina no son roca (no se pasa "entre" dos rocas) |

Las reglas se aplican con dos funciones:

| Función | Qué hace |
|---|---|
| `_desplazar` | Herramienta: da "lo que tiene la vecina" de todas las celdas a la vez |
| `_calcular_factibilidad` | Usa `_desplazar` para aplicar las 4 reglas en las 8 direcciones y guarda una tabla de sí/no |

#### 3.4.1 `_desplazar(matriz, di, dj, relleno)`

**Problema:** para cada celda quiero saber qué hay en **su vecina** en una
dirección (p. ej. la altura de la de la derecha). Con bucles
(`for i… for j… H[i, j+1]`) funciona, pero es lento y hay que vigilar los bordes.

**Idea:** devuelve una matriz **del mismo tamaño** en la que la casilla `(i, j)`
contiene **lo que tenía la vecina `(i+di, j+dj)`** en la original. Lo que
caería fuera del mapa se rellena con `relleno`.

Con letras:
```
Original:          Derecha (0, 1):     Arriba (-1, 0):     Diagonal ↘ (1, 1):
a  b  c            b  c  ·             ·  ·  ·             e  f  ·
d  e  f            e  f  ·             a  b  c             h  i  ·
g  h  i            h  i  ·             d  e  f             ·  ·  ·
```
- En "Derecha", el centro tenía `e` y ahora tiene **`f`**, su vecina de la derecha.
- En "Arriba", el centro tiene **`b`**, su vecina de arriba.
- La fila o columna que no tiene vecina queda con `·` (relleno).

**Para qué sirve:** restando dos matrices sale el desnivel de todas las celdas de golpe:
```
H:                  _desplazar(H, 0, 1)      resta = desnivel hacia la derecha
0.0  0.2  1.0       0.2  1.0  nan            0.2   0.8  nan
0.1  0.3  0.4       0.3  0.4  nan     →      0.2   0.1  nan
0.0  0.5  0.2       0.5  0.2  nan            0.5  -0.3  nan
```

**El relleno se elige a propósito:**
- alturas, con `nan`: cualquier cálculo con `nan` da `nan` y cualquier comparación da
  `False`, así que "fuera del mapa" nunca es factible (**regla i gratis**);
- rocas, con `True`: "fuera del mapa" cuenta como roca.

**Por dentro:**
```python
N, M = matriz.shape
resultado = np.full(matriz.shape, relleno, dtype=matriz.dtype)       # 1. todo a relleno
resultado[max(0, -di):N - max(0, di), max(0, -dj):M - max(0, dj)] = \
    matriz[max(0, di):N + min(0, di), max(0, dj):M + min(0, dj)]     # 2. copiar un trozo
```
1. Una matriz del mismo tamaño llena de relleno.
2. Copia **un trozo** del original en **otro trozo** del resultado. Los `max`/`min`
   solo calculan qué trozo con qué trozo (recordatorio: `M[0:2]` = filas 0 y 1,
   el final no se incluye).

Ejemplo **derecha** (`di = 0, dj = 1`, 3×3):

| | Filas | Columnas |
|---|---|---|
| **Destino** (resultado) | `0:3` (todas) | `max(0,-1) : 3-max(0,1)` → `0:2` (cols 0 y 1) |
| **Origen** (original) | `0:3` (todas) | `max(0,1) : 3+min(0,1)` → `1:3` (cols 1 y 2) |

*"Copia las columnas 1-2 del original en las columnas 0-1 del resultado"*; la
columna 2 se queda con relleno.

Ejemplo **arriba** (`di = -1, dj = 0`):

| | Filas |
|---|---|
| **Destino** | `max(0,1) : 3-max(0,-1)` → `1:3` (filas 1 y 2) |
| **Origen** | `max(0,-1) : 3+min(0,-1)` → `0:2` (filas 0 y 1) |

*"Copia las filas 0-1 del original en las filas 1-2 del resultado"*; la fila
0 se queda con relleno.

**Regla para no perderse:**
- `d = +1` (vecina hacia delante): el **origen** empieza en 1 y el **destino** acaba 1 antes;
- `d = -1` (vecina hacia atrás): el **destino** empieza en 1 y el **origen** acaba 1 antes;
- `d = 0`: todo entero.

#### 3.4.2 `_calcular_factibilidad(self)`

**Propósito:** contesta **de una vez y para todo el mapa** a *"desde (i, j),
¿puedo dar un paso en la dirección k?"* y **lo guarda en una tabla**. Cuando
A* pregunte "¿a qué vecinas puedo ir?" (cientos de miles de veces), solo mira
la tabla. Es como hacer la tabla de multiplicar una vez en vez de multiplicar
cada vez.

**Resultado: 8 mapas de sí/no**, uno por dirección:
```python
factible = np.zeros((len(DIRECCIONES),) + self.alturas.shape, dtype=bool)
```
```
factible[0] → ↖   factible[1] → ↑   factible[2] → ↗   factible[3] → ←
factible[4] → →   factible[5] → ↙   factible[6] → ↓   factible[7] → ↘
```
`factible[4, 10, 20] == True` significa "desde (10, 20) se puede ir a la derecha".

**El bucle:** una vuelta por dirección (`for k, (di, dj) in enumerate(DIRECCIONES)`).
Ejemplo: vuelta **derecha** `(0, 1)` con el `H` de arriba y **una roca en (1, 2)**.

**Paso 1: ver a la vecina**
```python
altura_vecina = _desplazar(self.alturas, di, dj, np.nan)
roca_vecina   = _desplazar(self.rocas,   di, dj, True)
```
```
roca_vecina:
F  F  T      ← (0,2): fuera del mapa → True
F  T  T      ← (1,1): su vecina (1,2) es roca → True
F  F  T
```

**Paso 2: desnivel y pendiente (regla iii)**
```python
desnivel = altura_vecina - self.alturas
pendiente = np.arctan(desnivel / self.distancia_horizontal(di, dj))
pendiente_ok = np.abs(pendiente) <= self.theta_max
```
```
desnivel:            pendiente:              ¿|θ| ≤ 25°?
 0.2   0.8   nan      11°    39°   nan        T  F  F
 0.2   0.1   nan      11°     6°   nan        T  T  F
 0.5  -0.3   nan      27°   -17°   nan        F  T  F
```
- `distancia_horizontal` = 1 m (diagonal: 1,41 m).
- `abs(...)`: subir o bajar más de 25° está igual de prohibido.
- `nan` da `False` automáticamente (regla i).
- `np.errstate(invalid="ignore")` silencia el warning de operar con `nan`
  (aquí es intencionado).

**Paso 3: rocas (regla ii)**
```python
ok = ~self.rocas & ~roca_vecina & pendiente_ok
```
`~` = NO, `&` = Y. Se lee: *"puedo ir si **yo no estoy en roca** Y **mi vecina no
es roca** Y **la pendiente está bien**"*.
```
~rocas:      ~roca_vecina:   pendiente_ok:      ok:
T  T  T      T  T  F         T  F  F            T  F  F
T  T  F      T  F  F    &    T  T  F     =      T  F  F    ← (1,1) ya no: vecina roca
T  T  T      T  T  F         F  T  F            F  T  F
```

**Paso 4: esquinas en diagonal (regla iv)**, solo en las 4 diagonales
```python
if di != 0 and dj != 0:
    ok &= ~_desplazar(self.rocas, di, 0, True)   # ¿la celda de arriba/abajo es roca?
    ok &= ~_desplazar(self.rocas, 0, dj, True)   # ¿la de izquierda/derecha es roca?
```
Al ir en diagonal se pasa "rozando" dos celdas. Si alguna es roca, no cabe:
```
 █  G        ✗ de S a G en diagonal no: se "colaría" entre dos rocas
 S  █
```
`ok &= ~…` = *"sigo pudiendo si ya podía Y esa celda no es roca"*.

**Paso 5: guardar.** `factible[k] = ok`. Tras 8 vueltas, la tabla está completa.

**¿Merece la pena?**
- **Rapidez:** 8 operaciones con matrices (numpy, en C) en vez de 320 000
  comprobaciones sueltas en Python (N = 200).
- **Memoria:** 8 × 200 × 200 valores `True`/`False` ≈ **320 KB**.
- **Uso:** `movimientos_factibles((i, j))` solo mira `factible[k, i, j]`.
- **Verificado:** `test_factibilidad_coincide_con_las_reglas` comprueba en 2000
  casos al azar que la tabla coincide con aplicar las 4 reglas a mano.

**Resumen:** *para cada una de las 8 direcciones se "mueve" el mapa una casilla
para ver a la vecina de todas las celdas a la vez, se comprueban las 4 reglas y
se guarda el resultado en una tabla de sí/no que la búsqueda consulta después.*

#### 3.4.3 Nota

**La factibilidad es simétrica** (`|θ(a,b)| = |θ(b,a)|`): si puedo ir de a a b,
puedo volver. Pero el **coste no** es simétrico (subir cuesta más que bajar);
eso irá en `problem.py`.

### 3.5 Elegir S y G y comprobar que hay camino

1. `S` = celda transitable al azar.
2. `alcanzables_desde(S)`: **búsqueda en anchura (BFS)** con una cola
   (`collections.deque`), que marca todas las celdas a las que se puede llegar.
   Aquí no importa el coste, solo si existe camino.
3. `G` = celda alcanzable al azar que esté a ≥ `0,7·N·s` de `S` (para que la
   ruta cruce buena parte del mapa).
4. Si no hay ninguna, se prueba otra `S`. Si tras varios intentos no hay
   ninguna, se **regenera el mapa** con el mismo `rng`, así que el resultado sigue
   dependiendo solo de la semilla.

### 3.6 Guardar y cargar mapas

- `np.savez_compressed` guarda varias matrices en **un solo archivo `.npz`**
  (es un zip de arrays): alturas, rocas, s, θ_max, S, G, semilla y los
  parámetros del generador (`param_*`).
- **No es una imagen.** Para verlo:
  ```python
  from terrain import cargar_terreno
  from visualizar_terreno import dibujar_terreno
  t = cargar_terreno("maps/terreno_N100_s0.npz")
  dibujar_terreno(t, "Mapa cargado", "mapa_cargado.png")   # -> figures/
  ```
- Para curiosear los datos: `np.load(ruta).files`.

---

## 4. problem.py — el problema de búsqueda y el coste

**Propósito:** el terreno dice **qué caminos existen** (qué pasos se pueden
dar). `problem.py` dice **cuánto cuesta cada paso**, en segundos. Es como un
mapa de carreteras: el terreno dibuja las carreteras, y `problem.py` pone
el tiempo que se tarda en recorrer cada tramo.

Aquí aparece lo más importante del modelo: la **asimetría**. Un mismo tramo
tarda más en subida que en bajada.

### 4.1 La interfaz del problema

`RoverProblem` sigue la clase `Problem` del libro y de aima-python [R6]. Los
nombres de los métodos van en inglés a propósito: son los que usa el libro,
y así `search.py` puede ser **genérico** (no sabe que resuelve un rover;
solo llama a estos 5 métodos).

| Método | Elemento de la formulación | Qué hace |
|---|---|---|
| `initial` / `goal` | Estado inicial / objetivo | S y G (del terreno, o los que se pasen, p. ej. para E4 ida/vuelta) |
| `actions(estado)` | Acciones | Pasos `(di, dj)` factibles, que pide a `terreno.movimientos_factibles` |
| `result(estado, accion)` | Modelo de transición | `(i + di, j + dj)` |
| `is_goal(estado)` | Test objetivo | `estado == G` |
| `action_cost(estado, accion, siguiente)` | Coste de acción | Tiempo del paso (4.3) |

`action_cost` recibe `accion` **y** `siguiente` aunque uno se deduzca del
otro: es la firma del libro (`c(s, a, s')`), y así se evitan recálculos.

Que `inicio` y `objetivo` sean opcionales sirve para planificar **al revés**
(de G a S) sobre el mismo terreno, en el experimento de asimetría:
```python
ida    = RoverProblem(terreno)                                   # S -> G
vuelta = RoverProblem(terreno, inicio=terreno.objetivo, objetivo=terreno.inicio)
```

### 4.2 `velocidad(theta)`

```python
def velocidad(theta):
    if theta >= 0:
        return V_MAX * (1 - K_SUB * theta / THETA_MAX)    # subida
    return V_MAX * (1 - K_BAJ * -theta / THETA_MAX)       # bajada
```

**Qué hace:** a qué velocidad va el rover según la pendiente del paso.
Es la ecuación de la velocidad de la memoria.

Paso a paso:
1. `theta / THETA_MAX` = **qué fracción de la pendiente máxima** es esta
   cuesta: 0 en llano, 1 en 25°.
2. `K_SUB * …` = **cuánta velocidad se pierde**: en subida, hasta el 80 %
   (`K_SUB = 0,8`); en bajada, hasta el 40 % (`K_BAJ = 0,4`).
3. `V_MAX * (1 - …)` = la velocidad que queda.
4. En bajada, `theta` es negativo, así que se usa `-theta` (el valor absoluto)
   para que la fracción salga positiva.

**Tabla de valores:**

| Pendiente θ | Fracción de θ_max | Pérdida | v (m/s) | v / v_max |
|---|---|---|---|---|
| −25° (bajada máx.) | 1 | 40 % | 0,0252 | 0,60 |
| −10° | 0,4 | 16 % | 0,0353 | 0,84 |
| 0° (llano) | 0 | 0 % | **0,0420** | **1,00** |
| +10° | 0,4 | 32 % | 0,0286 | 0,68 |
| +25° (subida máx.) | 1 | 80 % | 0,0084 | 0,20 |

Gráficamente:
```
 v
 v_max ─ ─ ─ ─ ─ ─ ─ ●  ← máximo solo en llano
                   ╱   ╲
  0,6·v_max  ●───╱       ╲         bajada: cae poco
                           ╲       subida: cae mucho
  0,2·v_max                  ●
           -25°      0°     +25°   θ
```

**Por qué es tan importante que `v ≤ v_max` siempre (Lema 1 de la memoria):**
las heurísticas calculan "distancia / `V_MAX`", es decir, el tiempo **yendo
lo más rápido posible**. Si el rover pudiera ir más rápido que `V_MAX` en
alguna bajada, la heurística podría **pasarse** (dejaría de ser admisible) y
A* podría devolver rutas que no son óptimas.

Por eso **no** se usa tal cual la función de Tobler para personas [R8]: en ella,
una bajada suave es *más rápida* que el llano, y eso rompería las heurísticas.

### 4.3 `action_cost` — el coste de un paso

```python
def action_cost(self, estado, accion, siguiente):
    d_h = self.terreno.distancia_horizontal(*accion)        # 1 m o 1,41 m
    desnivel = self.terreno.alturas[siguiente] - self.terreno.alturas[estado]
    theta = self.terreno.pendiente(estado, siguiente)       # con signo
    return math.hypot(d_h, desnivel) / velocidad(theta)     # tiempo = distancia / velocidad
```

Línea a línea:
1. **`d_h`**: distancia horizontal del paso. `*accion` "desempaqueta" la
   tupla `(di, dj)` en dos argumentos: `distancia_horizontal(di, dj)`.
2. **`desnivel`**: altura de destino menos altura de origen, **con signo**
   (+ sube, − baja).
3. **`theta`**: la pendiente con signo, calculada por el terreno (sección 3).
   Se reutiliza en vez de recalcularla aquí.
4. **`math.hypot(d_h, desnivel)`** = `√(d_h² + desnivel²)`: la distancia que
   recorre de verdad, **por la cuesta** (Pitágoras: la cuesta es la hipotenusa).
   Luego, **tiempo = distancia / velocidad**.

```
            ╱│
     d    ╱  │ desnivel
        ╱    │
      ╱──────┘
        d_h
```

**Ejemplo 1: paso diagonal en subida**, `(1,0) → (2,1)` del mapa 4×4:

| Magnitud | Cálculo | Valor |
|---|---|---|
| `d_h` | `1 · √2` | 1,414 m |
| `desnivel` | `0,5 − 0,2` | +0,3 m |
| `theta` | `atan(0,3 / 1,414)` | +11,98° |
| `v` | `0,042 · (1 − 0,8 · 11,98/25)` | 0,02590 m/s |
| `d` | `√(1,414² + 0,3²)` | 1,4457 m |
| **coste** | `1,4457 / 0,02590` | **55,81 s** |

**Ejemplo 2: la asimetría**, el mismo tramo `(0,0) ↔ (1,0)` (0,2 m de desnivel):

| | Subida `(0,0) → (1,0)` | Bajada `(1,0) → (0,0)` |
|---|---|---|
| θ | +11,31° | −11,31° |
| Pérdida de velocidad | 0,8 · 11,31/25 = 36 % | 0,4 · 11,31/25 = 18 % |
| v | 0,02680 m/s | 0,03440 m/s |
| d | 1,0198 m | 1,0198 m |
| **coste** | **38,05 s** | **29,65 s** |

La distancia es la misma, pero la velocidad no, así que **el mismo tramo
cuesta 8,4 s más en subida**. En el mapa 4×4 esto hace que la ruta óptima de
ida (166,82 s) y la de vuelta (170,14 s) sean **caminos distintos**.

**Rango de costes de un paso** (útil para interpretar resultados):

| Caso | Coste |
|---|---|
| Mínimo: recto y llano | `1 / 0,042` = **23,81 s** |
| Recto subiendo a 25° | `(1/cos 25°) / 0,0084` ≈ 131,4 s |
| Diagonal subiendo a 25° (máximo) | `(1,414/cos 25°) / 0,0084` ≈ 185,8 s |

El mínimo, 23,81 s = `s / V_MAX`, es el Lema 2 de la memoria: **ningún paso es
gratis**. Eso es lo que garantiza que UCS y A* terminan y son óptimos.

---

## 5. heuristics.py — las estimaciones

**Propósito:** A* necesita, en cada celda, una **estimación de cuánto tiempo
falta hasta G**. Es como el "tiempo estimado" de un GPS antes de conocer el
tráfico. La regla de oro es **no pasarse nunca** (ser *admisible*): si la
estimación es optimista, A* sigue encontrando la ruta óptima.

**Idea (relajación):** las tres se calculan "haciendo trampa" con el problema,
es decir, **quitándole dificultades**: como si el terreno fuera llano y sin
obstáculos, e yendo siempre a `V_MAX`. El tiempo en ese mundo fácil
**nunca puede ser mayor** que en el real, así que nunca se pasa.

Todas tienen la misma firma `h(estado, problema)`. Reciben el `problema`
porque necesitan saber dónde está `G` (`problema.goal`) y el tamaño de
celda (`problema.terreno.s`).

### 5.1 h0, h1 y h2

Primero, en `h1` y `h2`, cuántas filas y columnas faltan hasta G:
```python
di = abs(estado[0] - problema.goal[0])     # filas que faltan
dj = abs(estado[1] - problema.goal[1])     # columnas que faltan
```

| Heurística | Código | Qué "trampa" hace | Informada |
|---|---|---|---|
| `h0` | `0` | Ninguna estimación | Nada (A* = UCS) |
| `h1` | `s · hypot(di, dj) / V_MAX` | Llano, sin obstáculos y **en línea recta** (vuelo de pájaro) | Algo |
| `h2` | `s · (max + (√2−1)·min) / V_MAX` | Llano, sin obstáculos, pero **moviéndose por la cuadrícula** en 8 direcciones | Más |

**h1: distancia euclídea.** `math.hypot(di, dj) = √(di² + dj²)`, Pitágoras
otra vez. Es la distancia en línea recta, como si el rover pudiera ir en
cualquier ángulo.

**h2: distancia octil.** El rover no puede ir en cualquier ángulo, solo en 8
direcciones. El camino más corto por la cuadrícula es:
1. hacer **`min(di, dj)` pasos en diagonal** (cada uno avanza una fila Y una
   columna, y mide √2);
2. hacer **el resto (`max − min`) en recto** (cada uno mide 1).

Longitud = `min · √2 + (max − min) · 1` = **`max + (√2 − 1) · min`**
(se reordena para que quede más corta).

Ejemplo: de `(0,1)` a `(3,3)`, con `di = 3` y `dj = 2`:
```
 (0,1) ●
         ╲         2 diagonales (√2 cada una) = 2,83 m
           ╲
             ●
             │     1 recto (1 m)              = 1,00 m
             ● (3,3)                    total = 3,83 m
```
- `h2 = 3,83 / 0,042` = **91,15 s**
- `h1 = √(9 + 4) / 0,042 = 3,61 / 0,042` = **85,85 s** (la recta es más corta)
- El coste real `h*` es **138,35 s** (hay cuestas y una roca). Las dos se
  quedan cortas, que es justo lo que se busca, y `h2` se acerca más.

### 5.2 Por qué funcionan (admisibles, consistentes, h2 ≥ h1)

Resumen intuitivo de las demostraciones (Proposiciones 1–3 del `.tex`):

| Propiedad | Qué significa | Por qué se cumple |
|---|---|---|
| **Admisible** `h ≤ h*` | Nunca se pasa | El camino real mide al menos la distancia octil (y esta, al menos la euclídea); las cuestas solo lo alargan; y nunca se va más rápido que `V_MAX` |
| **Consistente** `h(a) ≤ c(a,b) + h(b)` | Al dar un paso, la estimación no baja más de lo que cuesta el paso | Cada paso cuesta al menos `d_h / V_MAX`, que es justo lo máximo que puede bajar la estimación (desigualdad triangular) |
| **Dominancia** `h2 ≥ h1` | h2 es más ajustada | Ir por la cuadrícula es igual o más largo que ir en línea recta |

**Por qué importa cada una:**
- **Admisible** implica que A* encuentra la ruta **óptima**.
- **Consistente** implica que, en búsqueda en grafo, la primera vez que A* saca
  un nodo de la cola **ya tiene su mejor coste**, así que no hay que reabrirlo.
  Esto simplifica `search.py`.
- **h2 ≥ h1** implica que A*(h2) **nunca expande más nodos** que A*(h1).

**¿Cuándo son iguales h1 y h2?** Cuando `min = 0` (G en la misma fila o
columna) o `max = min` (G en diagonal). Por ejemplo, desde `(0,0)` a `(3,3)`:
`h1 = h2 = 101,02 s`.

**¿Cuándo es h2 perfecta?** En terreno llano y sin obstáculos, `h2 = h*`
exactamente, porque ese es el problema relajado. En la traza del 4×4 se ve:
en los pasos llanos que van directos a G, `f = g + h2` no cambia.

**Límite:** con cuestas fuertes, el coste real puede ser hasta ~5,5 veces la
estimación (Lema 2), así que en mapas muy accidentados las heurísticas
ayudan menos. Hay que tenerlo en cuenta al interpretar los experimentos.

### 5.3 `ponderada(h, w)`

```python
def ponderada(heuristica, w):
    return lambda estado, problema: w * heuristica(estado, problema)
```

**Qué hace:** **fabrica una heurística nueva** que es la de siempre
multiplicada por `w`. Devuelve una función (con `lambda`), no un número:

```python
h2x2 = ponderada(h2, 2)     # h2x2 es una función nueva
h2x2((0, 1), problema)      # = 2 * h2((0, 1), problema) = 182,30 s
```

Así se le puede pasar a A* igual que `h1` o `h2`, sin tocar `search.py`.

**Para qué:** A* ponderado (añadido A1). Con `w > 1` la heurística **deja de
ser admisible** (se pasa), así que A* se vuelve más "ansioso" por ir hacia G:
expande menos nodos, pero la ruta puede no ser óptima. Garantía teórica
(Pohl 1970 [R10]): el coste obtenido es **como mucho `w` veces el óptimo**.
Con `w = 1,5`, la ruta cuesta como mucho un 50 % más.

### 5.4 Tests del paso 2

`tests/test_problem.py` (10 tests). El mapa 4×4 de la memoria está en
`tests/conftest.py` como *fixture* `mapa_4x4`, para reutilizarlo en los
tests de búsqueda.

| Test | Comprueba | Relación con la memoria |
|---|---|---|
| `test_velocidad_acotada` | `0,2·v_max ≤ v ≤ v_max`, `v(0) = v_max` | Lema 1 |
| `test_subir_es_mas_lento_que_bajar` | `v(θ) < v(−θ)` | Asimetría |
| `test_costes_del_ejemplo_4x4` | 38,05 · 55,81 · 39,03 · 23,81 s | Tabla de la ruta óptima |
| `test_coste_asimetrico` | Mismo tramo: 38,05 s frente a 29,65 s | Asimetría |
| `test_coste_minimo_positivo` | Todo paso ≥ 23,81 s en un mapa real | Lema 2 |
| `test_valores_del_ejemplo_4x4` | h1, h2 en celdas del 4×4 | Tabla de heurísticas |
| `test_admisibles_en_el_ejemplo_4x4` | `h1 ≤ h2 ≤ h*` en todas las celdas | Proposición 1 |
| `test_dominancia_e_igualdad` | `h2 ≥ h1`, iguales solo en fila/columna/diagonal | Proposición 3 |
| `test_consistencia_en_todas_las_aristas` | `h(a) ≤ c(a,b) + h(b)` en todos los pasos | Proposición 2 |
| `test_ponderada` | `ponderada(h2, 1,5) = 1,5·h2` | A1 |

---

## 6. Pasos pendientes

- [x] **Paso 2:** `problem.py`, `heuristics.py`
- [ ] **Paso 3:** `search.py`, `metrics.py` (+ `test_search.py` con el 4×4)
- [ ] **Paso 4:** `rover_agent.py`
- [ ] **Paso 5:** `run_experiments.py`, `make_figures.py`
- [ ] Ajustar el nº de cráteres para mapas pequeños (con N=100 y 12 cráteres
      se solapan mucho): quizá `n_crateres ∝ N²`.

---

## 7. Referencias

### Filtro gaussiano y ruido (relieve base)

- **[R1]** SciPy, `scipy.ndimage.gaussian_filter` (documentación oficial:
  parámetros `sigma`, `mode="reflect"`, `truncate`).
  https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.gaussian_filter.html
- **[R2]** Wikipedia, *Gaussian blur*: qué es el filtro, la fórmula del núcleo
  y por qué actúa como filtro paso bajo.
  https://en.wikipedia.org/wiki/Gaussian_blur
- **[R3]** Red Blob Games, *Making maps with noise functions*: generar mapas
  de alturas a partir de ruido, con ejemplos interactivos. Usa ruido de
  Perlin/simplex en vez de ruido suavizado, pero la idea es la misma y es
  muy visual.
  https://www.redblobgames.com/maps/terrain-from-noise/
- **[R4]** NumPy, `numpy.random.Generator.normal` y `default_rng` (semillas
  y reproducibilidad).
  https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.normal.html
  https://numpy.org/doc/stable/reference/random/generator.html
- **[R5]** Wikipedia, *Gaussian random field*: el concepto formal de
  "ruido blanco suavizado = campo aleatorio con correlación espacial".
  https://en.wikipedia.org/wiki/Gaussian_random_field

### Problema, coste y heurísticas (paso 2)

- **[R6]** aima-python, clase `Problem` en `search.py` (interfaz
  `actions` / `result` / `is_goal` / `action_cost`), que es la que sigue `RoverProblem`.
  https://github.com/aimacode/aima-python/blob/master/search.py
- **[R7]** Amit Patel, *Heuristics* (Amit's A\* Pages, Stanford): distancias
  Manhattan, **diagonal/octil** y euclídea en cuadrículas, cuándo usar cada
  una y el efecto de escalar la heurística. Es la referencia práctica más
  directa para `h1` y `h2`.
  http://theory.stanford.edu/~amitp/GameProgramming/Heuristics.html
- **[R8]** Wikipedia, *Tobler's hiking function*: función de velocidad en
  pendiente para personas. Sirve de contraste: en ella la bajada suave es más
  rápida que el llano, y por eso aquí se usa un modelo propio con `v ≤ v_max`.
  https://en.wikipedia.org/wiki/Tobler%27s_hiking_function
- **[R9]** Hart, Nilsson y Raphael (1968), *A formal basis for the heuristic
  determination of minimum cost paths*: el artículo original de A\*
  (admisibilidad y optimalidad). Ya citado en el `.tex`.
- **[R10]** Pohl (1970), *Heuristic search viewed as path finding in a graph*:
  A\* ponderado y la cota `C ≤ w·C*`. Likhachev et al. (2003), ARA\*: la misma
  cota sin reabrir nodos. Entradas `.bib` al final de
  `memoria/ej3_fase1_heuristicas.tex`.
- Russell & Norvig, *AIMA* 4.ª ed., §3.5.2 (A\*, admisibilidad,
  consistencia) y §3.6 (heurísticas, relajación, dominancia).
- Python, `math.hypot` (`√(x² + y²)` sin desbordamientos).
  https://docs.python.org/3/library/math.html#math.hypot

### Otros detalles de implementación

- NumPy, `numpy.savez_compressed` / `numpy.load` (formato `.npz`).
  https://numpy.org/doc/stable/reference/generated/numpy.savez_compressed.html
- Python, `collections.deque` (cola para la BFS).
  https://docs.python.org/3/library/collections.html#collections.deque
- Red Blob Games, *Introduction to the A\* Algorithm*: BFS, Dijkstra y A\*
  sobre cuadrículas, con animaciones. Útil para el paso 3.
  https://www.redblobgames.com/pathfinding/a-star/introduction.html
- aima-python, `search.py` (`best_first_graph_search`, `astar_search`):
  referencia para el paso 3 (citar si se reutiliza).
  https://github.com/aimacode/aima-python

### Del modelo (ya en el `.tex`)

- Russell & Norvig, *AIMA* 4.ª ed.: agentes (cap. 2), búsqueda (cap. 3).
- Krüger et al. (2018), Stopar et al. (2017): relación profundidad/diámetro de cráteres.
- Kirk et al. (2008): DTM de HiRISE a 1 m.

> Para la declaración de IAG / memoria: citar SciPy (`gaussian_filter`) y
> NumPy como herramientas. El generador es implementación propia.
