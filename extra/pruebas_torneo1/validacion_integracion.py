"""Validación adicional con Tournament original.

Autores: Arturo Pérez Noves y Alejandro González García. Grupo 1311, pareja 08.
No modifica el envío ni accede a la plataforma.
"""
import hashlib
import json
import math
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
MOTOR = Path('/tmp/p1_motor_original')
SUBMISSION_FOLDER = HERE.parent / 'entregas/entrega_1'
SUBMISSION = SUBMISSION_FOLDER / 'p1_1311_08_perez_gonzalez.py'
sys.path.insert(0, str(MOTOR))
from game import Player, TwoPlayerGameState, TwoPlayerMatch
from reversi import Reversi
from tournament import Tournament, StudentHeuristic
from strategy import RandomStrategy

class Dummy(StudentHeuristic):
    def get_name(self):
        return 'dummy'

    def evaluation_function(self, state):
        return self.dummy(123)

    def dummy(self, n):
        return n + 4

blocked = False

class CheckedMatch(TwoPlayerMatch):
    def play_match(self):
        scores = super().play_match()
        assert scores is not None and all(value >= 0 for value in scores)
        assert not self.initial_state.player1.strategy.timed_out
        assert not self.initial_state.player2.strategy.timed_out
        result['completed_matches'] += 1
        return scores

def create_match(a, b):
    game = Reversi(a, b, 8, 8)
    state = TwoPlayerGameState(game=game, initial_player=a).setup_match()
    if blocked:
        for pos in ((2, 1), (8, 2), (1, 7), (7, 8)):
            state.board[pos] = 'O'
    state.end_of_game, state.scores = game.score(state)
    return CheckedMatch(state, max_seconds_per_move=10, gui=False)

tour = Tournament(max_depth=1, init_match=create_match, max_evaluation_time=0.5)
loaded = tour.load_strategies_from_folder(str(SUBMISSION_FOLDER), max_strat=3)
classes = loaded[SUBMISSION.name]
assert [c.__name__ for c in classes] == ['Solution1', 'Solution2', 'Solution3']
assert len({c().get_name() for c in classes}) == 3
result = {'sha256': hashlib.sha256(SUBMISSION.read_bytes()).hexdigest(),
          'submission': str(SUBMISSION), 'classes': [c.__name__ for c in classes],
          'manual_checks': 0, 'completed_matches': 0, 'tournaments': []}

# Casos con resultados calculados independientemente del código del envío.
a = Player('black', RandomStrategy())
b = Player('white', RandomStrategy())
game = Reversi(a, b, 8, 8)
state = TwoPlayerGameState(game=game, initial_player=a).setup_match()
for board, expected in [
    ({(1, 1): 'B', (4, 1): 'W', (4, 4): 'B', (2, 1): 'O'}, (95., 20., 100./3)),
    ({(2, 2): 'B', (2, 1): 'W'}, (-20., -5., 0.)),
    ({(1, 1): 'O', (8, 8): 'O'}, (0., 0., 0.)),
]:
    state.board = board
    state.end_of_game = False
    state.scores = None
    for player, sign in ((a, 1), (b, -1)):
        state.player_max = player
        for cls, score in zip(classes, expected):
            assert math.isclose(cls().evaluation_function(state), sign * score)
            result['manual_checks'] += 1

# Victorias, derrotas y empate terminales, ambos jugadores MAX.
for black_count in (20, 32, 44):
    positions = [(x, y) for x in range(1, 9) for y in range(1, 9)]
    state.board = {p: 'B' if i < black_count else 'W' for i, p in enumerate(positions)}
    state.end_of_game, state.scores = game.score(state)
    assert state.end_of_game
    for player, sign in ((a, 1), (b, -1)):
        state.player_max = player
        difference = sign * (black_count - (64 - black_count))
        expected = 10000. + difference if difference > 0 else -10000. + difference if difference < 0 else 0.
        for cls in classes:
            assert cls().evaluation_function(state) == expected
            result['manual_checks'] += 1

print('Carga original y 36 casos manuales: OK', flush=True)
for use_obstacles in (False, True):
    blocked = use_obstacles
    start = time.perf_counter()
    scores, totals, names = tour.run({'submission': classes, 'baseline': [Dummy]},
                                    increasing_depth=False, n_pairs=1, allow_selfmatch=False)
    # Cada una de las tres estrategias juega dos veces: negras y blancas.
    assert len(names) == 4 and len(totals) == 4
    assert all(v in (0, 1, 2) for name, v in totals.items() if name.startswith('submission'))
    result['tournaments'].append({'board': 'obstacles' if blocked else 'standard',
                                 'games': 6, 'seconds': time.perf_counter() - start,
                                 'scores': scores, 'totals': totals, 'names': names})
    print('Tournament.run completo', result['tournaments'][-1], flush=True)

assert hashlib.sha256(SUBMISSION.read_bytes()).hexdigest() == result['sha256']
assert result['completed_matches'] == 12
(HERE / 'integracion_final.json').write_text(json.dumps(result, indent=2, ensure_ascii=False))
print('Integracion completa: OK, archivo sin modificar.', flush=True)
