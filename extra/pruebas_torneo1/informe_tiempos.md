# Comprobación de tiempos — entrega 1

Autores: Arturo Pérez Noves y Alejandro González García. Grupo 1311, pareja 08.

Fecha: 7 de octubre de 2026. Motor: ZIP original, sin modificar. Python 3.12.13; NumPy 2.5.3.

## Conclusión

El coste relativo cumple la orientación de 10× si se mide como el motor suministrado: `Heuristic.evaluate`, incluida la copia del estado. Ninguna heurística supera 1,073× la trivial en las medianas de los grupos probados. Las funciones aisladas sí superan 10×. Por ello no se puede garantizar el comportamiento del servidor sin conocer su protocolo o probar allí el envío. No se ha accedido a la plataforma ni consumido tokens.

Un límite absoluto de 10 segundos por turno no queda garantizado a profundidad 4: en una posición normal con 17 sucesores, incluso la trivial tardó 18,52 s con minimax sin poda. Las tres propuestas tardaron entre 18,33 y 18,53 s. Las sondas no interrumpen turnos: comprueban el límite de 0,5 s por evaluación, igual al de demo_tournament.py.

## Archivo comprobado

`/home/arthur/Desktop/IA/P1/practicas-IA/extra/entregas/entrega_1/p1_1311_08_perez_gonzalez.py`

SHA-256: `95e1c2266dc1556ba71b5daf15f45f55c0b0b610afebf8972145402acfc783d4`. Coincide byte a byte con el fichero homónimo en la raíz de juegos. La carga dinámica de Tournament original detectó exactamente Solution1, Solution2 y Solution3, con nombres distintos. Sólo importa game, tournament y __future__; no hace llamadas al sistema ni modifica el estado en evaluación.

game.py, reversi.py, heuristic.py y demo_tournament.py locales coinciden con el ZIP. strategy.py y tournament.py locales están modificados; las mediciones usan sus versiones originales del ZIP.

## Tiempo por evaluación

Cada rango reúne las medianas de siete repeticiones en apertura, medio juego, final y estados terminales de ambos tableros. Se usan hasta doce estados por grupo. Los cocientes comparan el mismo grupo con Heuristic1; no son cocientes entre extremos de rangos diferentes.

| Heurística | Función sola (µs) | Mayor cociente sola | Con copia (µs) | Mayor cociente con copia |
|---|---:|---:|---:|---:|
| 1311_08_posicional | 1.73–6.88 | 83.30× | 94.45–166.70 | 1.073× |
| 1311_08_esquinas_bordes | 1.69–9.09 | 108.89× | 93.30–168.28 | 1.071× |
| 1311_08_paridad_fichas | 1.55–3.15 | 37.39× | 90.88–167.04 | 1.060× |

La función trivial aislada tarda aproximadamente 0,082–0,096 µs; con copia, 89,47–165,11 µs. La copia explica la diferencia entre ambos criterios. El motor original cronometra antes y después de `self.heuristic.evaluate(state)`, y esta función clona el estado antes de llamar a la evaluación del estudiante. El umbral 10× del enunciado es orientativo, no una garantía de aceptación.

## Búsquedas completas

Se probaron tablero normal y obstáculos B1, H2, A7, G8, bloqueando capturas, en apertura, una posición de ramificación alta y final, a profundidades 3 y 4. Son 48 búsquedas: cuatro evaluadores incluyendo la trivial. Todas devolvieron movimientos legales y ninguna activó timed_out por evaluación. Una sola medición por combinación: sirve para comprobar funcionamiento y orden de magnitud, no para afirmar mejoras pequeñas.

| Tablero / posición | Profundidad | Trivial (s) | Posicional (s) | Esquinas/bordes (s) | Fichas (s) |
|---|---:|---:|---:|---:|---:|
| standard / initial | 3 | 0.0159 | 0.0169 | 0.0160 | 0.0160 |
| standard / initial | 4 | 0.0743 | 0.0759 | 0.0762 | 0.0790 |
| standard / high_branching | 3 | 1.5125 | 1.5427 | 1.5168 | 1.5191 |
| standard / high_branching | 4 | 18.5182 | 18.5210 | 18.5295 | 18.3258 |
| standard / late | 3 | 0.0183 | 0.0175 | 0.0176 | 0.0179 |
| standard / late | 4 | 0.0344 | 0.0365 | 0.0369 | 0.0346 |
| obstacles / initial | 3 | 0.0252 | 0.0254 | 0.0255 | 0.0272 |
| obstacles / initial | 4 | 0.1142 | 0.1169 | 0.1168 | 0.1140 |
| obstacles / high_branching | 3 | 1.1340 | 1.1930 | 1.2025 | 1.1442 |
| obstacles / high_branching | 4 | 11.2438 | 11.8155 | 11.6595 | 11.4790 |
| obstacles / late | 3 | 0.0475 | 0.0451 | 0.0464 | 0.0445 |
| obstacles / late | 4 | 0.1679 | 0.1739 | 0.1732 | 0.1690 |

## Funcionamiento y partidas completas

476 estados legales obtenidos de ocho partidas aleatorias, cuatro por tablero. 1428 comprobaciones de heurísticas: valores finitos, estado sin modificar, signo opuesto al cambiar MAX y signo correcto en terminales.

Sesenta partidas completas con minimax original a profundidad 1 frente a evaluación aleatoria uniforme, ambos colores, ambos tableros y cinco semillas por color. Cero errores, sin activar timed_out; no se reproduce el mecanismo de interrupción por turno de TwoPlayerMatch, sino que se registra cada tiempo de state.move.

| Heurística | Tablero normal V/E/D | Obstáculos V/E/D | Máximo por turno (s) |
|---|---:|---:|---:|
| 1311_08_posicional | 9/1/0 | 6/1/3 | 0.0089 |
| 1311_08_esquinas_bordes | 8/0/2 | 7/0/3 | 0.0074 |
| 1311_08_paridad_fichas | 7/0/3 | 5/0/5 | 0.0087 |

Esta muestra de veinte partidas por heurística no equivale a los 1000 enfrentamientos oficiales ni permite predecir el ranking. La heurística de fichas ganó 5 de 10 partidas con obstáculos: conviene revisar su fuerza para los siguientes torneos aunque su coste de evaluación sea bajo.

## Entrega y plataforma

Según el enunciado facilitado, el primer torneo exige subir antes del 7 de octubre a las 20:00 en Madrid (18:00 UTC). El texto de Home facilitado no muestra ninguna fila de envío; no acredita una subida. La preparación del fichero y las pruebas locales no son participación confirmada. Hay que subir el fichero y comprobar el resultado de validación de la plataforma.

El fichero a subir es el de entrega_1, no la carpeta de pruebas ni un ZIP. Un torneo interno consume un token; ninguna prueba realizada aquí los consume.

## Reproducción

Consultar README.txt y verificar_tiempos.py en esta carpeta. resultados_original.json conserva las mediciones individuales; carga_original.json recoge las clases detectadas por el cargador original.
