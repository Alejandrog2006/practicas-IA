"""Pruebas locales de entrega 1, sin subir archivos ni gastar tokens.

Autores: Arturo Pérez Noves y Alejandro González García. Grupo 1311, pareja 08.
Uso: python3 verificar_tiempos.py --motor /tmp/p1_motor_original
"""
import argparse
import ast
import hashlib
import importlib.util
import inspect
import json
import math
import platform
import random
import statistics
import sys
import time
import timeit
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--motor', required=True)
parser.add_argument('--salida', default='resultados_original.json')
args = parser.parse_args()
HERE = Path(__file__).resolve().parent
SUBMISSION = HERE.parent / 'entregas/entrega_1/p1_1311_08_perez_gonzalez.py'
sys.path.insert(0, str(Path(args.motor).resolve()))
from game import Player, TwoPlayerGameState
from heuristic import Heuristic
from reversi import Reversi
from strategy import MinimaxStrategy
from tournament import StudentHeuristic, Tournament
import numpy as np

spec = importlib.util.spec_from_file_location('entrega1', SUBMISSION)
submission = importlib.util.module_from_spec(spec)
spec.loader.exec_module(submission)
# Cargar exactamente Heuristic1 sin ejecutar el torneo al importar la demo.
tree = ast.parse((Path(args.motor) / 'demo_tournament.py').read_text())
node = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Heuristic1')
scope = {'StudentHeuristic': StudentHeuristic, 'TwoPlayerGameState': TwoPlayerGameState}
exec(compile(ast.Module(body=[node], type_ignores=[]), 'Heuristic1_original', 'exec'), scope)
Dummy = scope['Heuristic1']
classes = [c for name, c in inspect.getmembers(submission, inspect.isclass)
           if c is not StudentHeuristic and issubclass(c, StudentHeuristic)]
assert len(classes) == 3
objects = [Dummy()] + [c() for c in classes]
OBSTACLES = ((2, 1), (8, 2), (1, 7), (7, 8))
result = {'python': sys.version, 'platform': platform.platform(), 'numpy': np.__version__,
          'motor': str(Path(args.motor).resolve()), 'submission': str(SUBMISSION),
          'sha256': hashlib.sha256(SUBMISSION.read_bytes()).hexdigest(),
          'obstacles': OBSTACLES, 'benchmarks': [], 'moves': [], 'random_games': []}

def save():
    (HERE / args.salida).write_text(json.dumps(result, indent=2, ensure_ascii=False))

def initial(blocked=False, functions=None):
    functions = functions or [objects[0].evaluation_function] * 2
    players = [Player(str(i), MinimaxStrategy(Heuristic(str(i), f), 1,
                      max_sec_per_evaluation=0.5)) for i, f in enumerate(functions)]
    game = Reversi(players[0], players[1], 8, 8)
    state = TwoPlayerGameState(game=game, initial_player=players[0]).setup_match()
    if blocked:
        for pos in OBSTACLES:
            state.board[pos] = 'O'
    state.end_of_game, state.scores = game.score(state)
    return state

states = []
sample_moves = []
for blocked in (False, True):
    trajectories = []
    for seed in range(4):
        rng = random.Random(1000 + seed)
        state = initial(blocked)
        trajectory = []
        while not state.end_of_game:
            trajectory.append(state)
            state = rng.choice(state.game.generate_successors(state)).setup_match()
        trajectory.append(state)
        trajectories.append(trajectory)
        states.extend((blocked, s) for s in trajectory)
    trajectory = trajectories[0]
    middle = [s for s in trajectory if 20 <= sum(v in ('B', 'W') for v in s.board.values()) <= 45]
    peak = max(middle, key=lambda s: len(s.game.generate_successors(s)))
    for phase, state in [('initial', trajectory[0]), ('high_branching', peak),
                         ('late', trajectory[-9])]:
        sample_moves.append((blocked, phase, state))

# Comprobación de pureza, finitud y perspectiva para ambos colores.
checks = 0
for blocked, state in states:
    board_before = dict(state.board)
    max_before = state.player_max
    next_before = state.next_player
    scores_before = state.scores.copy()
    for obj in objects[1:]:
        a = obj.evaluation_function(state)
        assert math.isfinite(a)
        assert state.board == board_before and state.next_player is next_before
        assert state.player_max is max_before and np.array_equal(state.scores, scores_before)
        state.player_max = state.game.opponent(max_before)
        b = obj.evaluation_function(state)
        state.player_max = max_before
        assert a == -b
        if state.end_of_game:
            diff = state.scores[0] - state.scores[1]
            if max_before.label == state.player2.label:
                diff = -diff
            assert (a > 0) == (diff > 0) and (a < 0) == (diff < 0)
        checks += 1
result['validation'] = {'states': len(states), 'heuristic_checks': checks,
                        'finite_pure_antisymmetric_terminal': True}
print('VALIDACION', result['validation'], flush=True)

# Misma colección de estados para todos, sin generación de jugadas en la medición.
for blocked in (False, True):
    trajectory = [s for flag, s in states if flag == blocked]
    groups = {'early': [], 'middle': [], 'late': [], 'terminal': []}
    for state in trajectory:
        occupied = sum(v in ('B', 'W') for v in state.board.values())
        phase = 'terminal' if state.end_of_game else 'early' if occupied < 20 else 'middle' if occupied < 45 else 'late'
        groups[phase].append(state)
    for phase, group in groups.items():
        sample = group[::max(1, len(group) // 12)][:12]
        for wrapped in (False, True):
            measurements = []
            # Repeticiones intercaladas para reducir el efecto de deriva térmica/carga.
            timing = [[] for _ in objects]
            functions = [Heuristic(o.get_name(), o.evaluation_function).evaluate if wrapped
                         else o.evaluation_function for o in objects]
            number = 120 if wrapped else 2000
            for repeat in range(7):
                order = list(range(len(functions)))
                random.Random(repeat).shuffle(order)
                for index in order:
                    fn = functions[index]
                    def batch():
                        for s in sample:
                            fn(s)
                    duration = timeit.timeit(batch, number=number)
                    timing[index].append(duration / (number * len(sample)))
            baseline = statistics.median(timing[0])
            for obj, times in zip(objects, timing):
                row = {'board': 'obstacles' if blocked else 'standard', 'phase': phase,
                       'wrapped': wrapped, 'name': obj.get_name(), 'states': len(sample),
                       'us_median': statistics.median(times) * 1e6,
                       'ratio_dummy': statistics.median(times) / baseline,
                       'us_min': min(times) * 1e6, 'us_max': max(times) * 1e6}
                result['benchmarks'].append(row)
            print('TIEMPOS', blocked, phase, 'con copia' if wrapped else 'funcion sola',
                  [(o.get_name(), round(statistics.median(t) / baseline, 2)) for o, t in zip(objects, timing)], flush=True)
            save()

# Jugadas completas con minimax ORIGINAL (sin poda), profundidades 3 y 4.
for blocked, phase, state in sample_moves:
    for depth in (3, 4):
        for obj in objects:
            state.player_max = state.next_player
            strategy = MinimaxStrategy(Heuristic(obj.get_name(), obj.evaluation_function), depth,
                                       max_sec_per_evaluation=0.5)
            t0 = time.perf_counter()
            successor = strategy.next_move(state)
            elapsed = time.perf_counter() - t0
            legal = state.game.generate_successors(state)
            assert any(s.board == successor.board and s.move_code == successor.move_code for s in legal)
            row = {'board': 'obstacles' if blocked else 'standard', 'phase': phase,
                   'depth': depth, 'name': obj.get_name(), 'seconds': elapsed,
                   'branching': len(legal), 'timed_out': strategy.timed_out}
            result['moves'].append(row)
            print('JUGADA', row, flush=True)
            save()

# Partidas enteras a profundidad 1 frente a evaluación aleatoria, ambos colores.
for blocked in (False, True):
    for obj in objects[1:]:
        for color in (0, 1):
            for seed in range(5):
                np.random.seed(7000 + seed)
                def random_eval(state):
                    return float(np.random.rand())
                funcs = [random_eval, random_eval]
                funcs[color] = obj.evaluation_function
                state = initial(blocked, funcs)
                max_move = 0
                ply = 0
                while not state.end_of_game:
                    t0 = time.perf_counter()
                    state = state.move()
                    max_move = max(max_move, time.perf_counter() - t0)
                    ply += 1
                    assert ply < 130
                    assert all(state.board.get(pos) == 'O' for pos in OBSTACLES) if blocked else True
                    assert not state.player1.strategy.timed_out and not state.player2.strategy.timed_out
                diff = state.scores[color] - state.scores[1-color]
                row = {'board': 'obstacles' if blocked else 'standard', 'name': obj.get_name(),
                       'color': 'black' if color == 0 else 'white', 'seed': seed,
                       'outcome': 'win' if diff > 0 else 'loss' if diff < 0 else 'draw',
                       'scores': state.scores.tolist(), 'plies': ply, 'max_move_seconds': max_move}
                result['random_games'].append(row)
        print('PARTIDAS', blocked, obj.get_name(),
              [r['outcome'] for r in result['random_games'] if r['name'] == obj.get_name()
               and r['board'] == ('obstacles' if blocked else 'standard')], flush=True)
        save()
print('COMPLETADO', HERE / args.salida, flush=True)
