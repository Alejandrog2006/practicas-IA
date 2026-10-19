README Práctica 1 IA
====================

Archivos adicionales a los iniciales:

- p1_1311_08_perez_gonzalez.py: implementación de las tres heurísticas.
- test_p1_1311_08_perez_gonzalez.py: pruebas unitarias.
- benchmark_heuristics.py: benchmark reproducible de las heurísticas.
- README.txt: instrucciones de ejecución y validación.
- memoria.pdf: memoria de la práctica.

El fichero p1_1311_08_perez_gonzalez.py contiene las tres heurísticas que se presentan al torneo:

- JeanDelPozoHeuristic
- IMSERSOheuristic
- Bulin47Heuristic

El benchmark usa siempre profundidad minimax 4, que es la profundidad máxima
indicada en el enunciado de la práctica.


Pruebas unitarias
-----------------

PYTHONPATH=p1_1311_08_perez_gonzalez .venv/bin/python -m unittest discover \
  -s p1_1311_08_perez_gonzalez \
  -p 'test_p1_1311_08_perez_gonzalez.py'

También se pueden ejecutar desde la carpeta de la práctica:

cd p1_1311_08_perez_gonzalez
PYTHONPATH=. ../.venv/bin/python -m unittest discover \
  -s . \
  -p 'test_p1_1311_08_perez_gonzalez.py'

Las pruebas comprueban:

- la API StudentHeuristic;
- los nombres públicos de las tres clases;
- que la evaluación devuelve un float;
- que la evaluación cambia correctamente al cambiar el jugador MAX;
- la evaluación terminal;
- la fórmula de final de Bulin47Heuristic.

En el caso de final utilizado por la prueba hay 40 fichas negras y
24 blancas. Bulin47Heuristic entra en la rama:

150 * (pieces_max - pieces_min) + positional

El resultado esperado es 2440.0 para ese tablero concreto.


Benchmark oficial
-----------------

Para ejecutar el benchmark con los dos tableros iniciales oficiales:

PYTHONPATH=p1_1311_08_perez_gonzalez .venv/bin/python \
  p1_1311_08_perez_gonzalez/benchmark_heuristics.py

El comando ejecuta profundidad 4 automáticamente y enfrenta cada pareja de
heurísticas en:

1. el tablero estándar;
2. el tablero con obstáculos en B1, H2, A7 y G8.

También alterna el jugador que comienza. La salida incluye cada partida, el
tiempo empleado y una clasificación por puntos:

- victoria: 3 puntos;
- empate: 1 punto para cada jugador;
- derrota: 0 puntos.

El benchmark muestra el progreso antes de comenzar cada partida. Por defecto
ejecuta las 12 partidas de los dos tableros oficiales y permite hasta 30
segundos por movimiento. Para una comprobación rápida a profundidad 4:

PYTHONPATH=p1_1311_08_perez_gonzalez .venv/bin/python \
  p1_1311_08_perez_gonzalez/benchmark_heuristics.py \
  --depth 4 \
  --max-games 2 \
  --max-seconds-per-move 10

Para ejecutar las 12 partidas completas con un límite de 30 segundos por
movimiento:

PYTHONPATH=p1_1311_08_perez_gonzalez .venv/bin/python \
  p1_1311_08_perez_gonzalez/benchmark_heuristics.py \
  --depth 4 \
  --max-seconds-per-move 30


Benchmark con posiciones aleatorias
-----------------------------------

El benchmark puede generar posiciones reproducibles de medio juego, pero
también mantiene profundidad 4:

PYTHONPATH=p1_1311_08_perez_gonzalez .venv/bin/python \
  p1_1311_08_perez_gonzalez/benchmark_heuristics.py \
  --depth 4 \
  --positions 4 \
  --plies 4 \
  --seed 131108 \
  --random-positions

La opción --depth se acepta por claridad, pero cualquier valor distinto de
4 se rechaza para evitar comparar resultados con una configuración diferente
de la del torneo.


Validación adicional
--------------------

Para comprobar sintaxis y espacios:

PYTHONPATH=p1_1311_08_perez_gonzalez .venv/bin/python -m py_compile \
  p1_1311_08_perez_gonzalez/p1_1311_08_perez_gonzalez.py \
  p1_1311_08_perez_gonzalez/benchmark_heuristics.py \
  p1_1311_08_perez_gonzalez/test_p1_1311_08_perez_gonzalez.py

git diff --check

El benchmark no modifica la implementación de las heurísticas. Solo importa
las tres clases, construye partidas reproducibles y recoge sus resultados.
