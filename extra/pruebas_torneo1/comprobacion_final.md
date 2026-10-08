# Última comprobación antes de subir — entrega 1

Autores: Arturo Pérez Noves y Alejandro González García. Grupo 1311, pareja 08.

Resultado: todas las comprobaciones locales han pasado. Se ha utilizado el motor original de extra/juegos.zip, verificado byte a byte, con Python 3.12.13 y NumPy 2.5.3. No se ha modificado el fichero de envío ni accedido a la plataforma.

Archivo: `/home/arthur/Desktop/IA/P1/practicas-IA/extra/entregas/entrega_1/p1_1311_08_perez_gonzalez.py`

SHA-256 antes y después: `d070f02c52b3751896e9479893227a9ba1efe5be3abeda8f5c9be0600d5b8d02`

## Comprobaciones realizadas

- Sintaxis e importación correctas; exactamente tres clases StudentHeuristic y tres nombres distintos.
- Carga dinámica real mediante load_strategies_from_folder de Tournament original.
- 1.428 comprobaciones en 476 estados legales: valor finito, tablero y estado sin modificar, perspectiva de ambos colores y signo terminal.
- 36 comprobaciones con valores esperados calculados independientemente: posiciones, bordes, obstáculos, victoria, derrota y empate terminal.
- 48 búsquedas completas sin poda, profundidades 3 y 4, ambos tableros, apertura, medio juego con 17 sucesores y final. Todas devolvieron una jugada legal, sin timeout por evaluación.
- 60 partidas completas a profundidad 1 contra evaluación aleatoria, ambos colores y tableros.
- 12 partidas adicionales mediante Tournament.run original y TwoPlayerMatch a profundidad 1 contra la trivial, ambos colores y tableros. Terminaron con puntuaciones válidas, sin timeout por evaluación ni superar el límite de 10 segundos por turno.

## Tiempos

| Heurística | Mayor cociente respecto a Heuristic1 con copia de estado |
|---|---:|
| 1311_08_posicional | 1.069× |
| 1311_08_esquinas_bordes | 1.062× |
| 1311_08_paridad_fichas | 1.033× |

Máximo tiempo por turno en las 60 partidas contra random a profundidad 1: 0.008662 s.

La evaluación completa del motor original incluye state.clone y queda por debajo del umbral orientativo de 10×. Las funciones aisladas superan 10×; no se conoce el protocolo del servidor. En posiciones de alta ramificación a profundidad 4, minimax sin poda tarda unos 18 segundos también con la trivial. Las sondas a profundidades 3 y 4 no imponen un límite absoluto por turno, sólo el de 0,5 segundos por evaluación. No se garantiza un límite de 10 segundos por turno a profundidad 4.

No se han jugado partidas completas a profundidad 4. Las 72 partidas completas son a profundidad 1. Esta validación prueba funcionamiento local, no garantiza el ranking ni la aceptación del servidor.

Los únicos cambios detectados respecto a la copia anteriormente comprobada son textos de cabecera y documentación; la última prueba utiliza la huella actual indicada arriba.

## Evidencia y reproducción

- resultados_comprobacion_final.json: estados, mediciones y 60 partidas.
- integracion_final.json: carga, 36 casos manuales y 12 partidas de integración.
- verificar_tiempos.py: ejecutar con --motor /tmp/p1_motor_original --salida resultados_comprobacion_final.json.
- validacion_integracion.py: ejecutar desde /tmp/p1_motor_original con Python 3.12 y NumPy.
- resultados_original.json e informe_tiempos.md se conservan como resultados históricos de la primera comprobación.
