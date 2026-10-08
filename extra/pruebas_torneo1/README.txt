Pruebas locales de tiempos de la entrega 1
Autores: Arturo Pérez Noves y Alejandro González García
Grupo: 1311. Pareja: 08.

verificar_tiempos.py carga exclusivamente entregas/entrega_1/
p1_1311_08_perez_gonzalez.py y utiliza el motor indicado por --motor.
No modifica las heurísticas, no contacta con la plataforma ni consume tokens.
No importa demo_tournament.py completo: extrae su clase Heuristic1 mediante AST
para evitar lanzar el torneo de demostración al importar el módulo.

Reproducción con Python 3.12, numpy y tkinter instalados:
1. Extraer extra/juegos.zip a una carpeta temporal, por ejemplo /tmp/p1_motor_original.
2. Desde esa carpeta, ejecutar:
   python3 /ruta/extra/pruebas_torneo1/verificar_tiempos.py \
     --motor /tmp/p1_motor_original --salida resultados_original.json

Protocolo:
- Ocho partidas aleatorias reproducibles (4 por tablero) generan estados legales.
- Se comprueba finitud, ausencia de cambios en el estado, inversión de signo al
  cambiar MAX y signo correcto de la valoración terminal.
- Se comparan la función sola y Heuristic.evaluate (incluye state.clone).
- Se separan apertura (<20 fichas), medio juego (20-44), final (>=45) y terminales.
- Cada grupo contiene hasta 12 estados. Siete repeticiones con orden intercalado.
- timeit: 2000 recorridos por repetición para función sola, 120 con copia.
- Se mide una jugada completa por combinación de tablero, fase, profundidad
  (3 y 4) y heurística, con MinimaxStrategy, sin poda. No se aplica un límite
  absoluto al turno en estas sondas; se mantiene el límite de 0,5 s/evaluación.
- Se juegan 60 partidas completas a profundidad 1 contra evaluación aleatoria,
  con ambos colores, ambos tableros y cinco semillas. Es una muestra exploratoria,
  no los 1000 enfrentamientos oficiales.

Resultados:
- resultados_original.json: mediciones, comprobaciones y partidas completas.
- carga_original.json: carga de las tres clases por Tournament original.
- informe_tiempos.md: interpretación de resultados y límites de las conclusiones.

Entorno utilizado: Python 3.12.13, numpy 2.5.3. Se usó numpy de la caché local
porque la instalación de red no estaba disponible. No se alteró el motor del ZIP.
Los tiempos absolutos dependen del equipo; los cocientes se calculan sobre los
mismos estados y con el mismo protocolo para cada heurística.
La carga dinámica se comprobó adicionalmente con load_strategies_from_folder
del Tournament original, sobre la carpeta entrega_1 y max_strat=3.
