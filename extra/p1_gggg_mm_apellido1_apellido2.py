"""Funciones de evaluacion heuristica para el torneo de Reversi.

ENTREGA 1 (Torneo 1 - 7 de Octubre):
    - Solution1: Evaluacion posicional basada en matriz estatica de pesos.
    - Solution2: Evaluacion geometrica basada en control de esquinas y bordes.
    - Solution3: Evaluacion cuantitativa basada en recuento y paridad de fichas.

Autores:
    Arturo Perez Noves <arturo.perezn@estudiante.uam.es>
    Alejandro Gonzalez Garcia <alejandro.gonzalez06@estudiante.uam.es>

Grupo: 1311
Pareja: 08
"""

from __future__ import annotations

from game import TwoPlayerGameState
from tournament import StudentHeuristic


# Coordenadas de las 4 esquinas del tablero 8x8
CORNERS = ((1, 1), (8, 1), (1, 8), (8, 8))

# Matriz estatica de ponderacion posicional para Reversi 8x8
WEIGHT_MATRIX = {
    (1, 1): 100, (2, 1): -20, (3, 1): 10, (4, 1): 5, (5, 1): 5, (6, 1): 10, (7, 1): -20, (8, 1): 100,
    (1, 2): -20, (2, 2): -40, (3, 2): -2, (4, 2): -2, (5, 2): -2, (6, 2): -2, (7, 2): -40, (8, 2): -20,
    (1, 3):  10, (2, 3):  -2, (3, 3):  1, (4, 3): 0, (5, 3): 0, (6, 3):  1, (7, 3):  -2, (8, 3):  10,
    (1, 4):   5, (2, 4):  -2, (3, 4):  0, (4, 4): 0, (5, 4): 0, (6, 4):  0, (7, 4):  -2, (8, 4):   5,
    (1, 5):   5, (2, 5):  -2, (3, 5):  0, (4, 5): 0, (5, 5): 0, (6, 5):  0, (7, 5):  -2, (8, 5):   5,
    (1, 6):  10, (2, 6):  -2, (3, 6):  1, (4, 6): 0, (5, 6): 0, (6, 6):  1, (7, 6):  -2, (8, 6):  10,
    (1, 7): -20, (2, 7): -40, (3, 7): -2, (4, 7): -2, (5, 7): -2, (6, 7): -2, (7, 7): -40, (8, 7): -20,
    (1, 8): 100, (2, 8): -20, (3, 8): 10, (4, 8): 5, (5, 8): 5, (6, 8): 10, (7, 8): -20, (8, 8): 100,
}


def _get_player_labels(state: TwoPlayerGameState):
    """Devuelve las etiquetas del jugador MAX y del adversario MIN."""
    if state.is_player_max(state.player1):
        return state.player1.label, state.player2.label
    return state.player2.label, state.player1.label


def _eval_terminal(state: TwoPlayerGameState):
    """Comprueba si el estado es terminal y devuelve el valor correspondiente."""
    if state.end_of_game:
        scores = state.scores
        if scores is not None:
            max_label, _ = _get_player_labels(state)
            if state.player1.label == max_label:
                diff = scores[0] - scores[1]
            else:
                diff = scores[1] - scores[0]
            if diff > 0:
                return True, 10000.0 + diff
            elif diff < 0:
                return True, -10000.0 + diff
            return True, 0.0
    return False, 0.0


class Solution1(StudentHeuristic):
    """Heuristica 1: Evaluacion posicional.
    
    Analiza la calidad de las posiciones ocupadas en el tablero mediante
    una matriz estatica de pesos.
    """

    def get_name(self) -> str:
        return "1311_08_posicional"

    def evaluation_function(self, state: TwoPlayerGameState) -> float:
        is_term, term_val = _eval_terminal(state)
        if is_term:
            return term_val

        max_label, min_label = _get_player_labels(state)
        pos_score = 0.0

        for pos, piece in state.board.items():
            if piece == max_label:
                pos_score += WEIGHT_MATRIX.get(pos, 0)
            elif piece == min_label:
                pos_score -= WEIGHT_MATRIX.get(pos, 0)

        return float(pos_score)


class Solution2(StudentHeuristic):
    """Heuristica 2: Control de esquinas y bordes.
    
    Se centra exclusivamente en la estabilidad de las piezas: las esquinas
    son permanentes e involteables, y los bordes ofrecen anclajes defensivos.
    """

    def get_name(self) -> str:
        return "1311_08_esquinas_bordes"

    def evaluation_function(self, state: TwoPlayerGameState) -> float:
        is_term, term_val = _eval_terminal(state)
        if is_term:
            return term_val

        max_label, min_label = _get_player_labels(state)
        corners_max = 0
        corners_min = 0
        edges_max = 0
        edges_min = 0

        for (x, y), piece in state.board.items():
            if piece == max_label:
                if (x, y) in CORNERS:
                    corners_max += 1
                elif x == 1 or x == 8 or y == 1 or y == 8:
                    edges_max += 1
            elif piece == min_label:
                if (x, y) in CORNERS:
                    corners_min += 1
                elif x == 1 or x == 8 or y == 1 or y == 8:
                    edges_min += 1

        score_corners = 25.0 * (corners_max - corners_min)
        score_edges = 5.0 * (edges_max - edges_min)

        return float(score_corners + score_edges)


class Solution3(StudentHeuristic):
    """Heuristica 3: Paridad de fichas.
    
    Evalua directamente la diferencia porcentual entre el numero de fichas propias
    y del adversario.
    """

    def get_name(self) -> str:
        return "1311_08_paridad_fichas"

    def evaluation_function(self, state: TwoPlayerGameState) -> float:
        is_term, term_val = _eval_terminal(state)
        if is_term:
            return term_val

        max_label, min_label = _get_player_labels(state)
        coins_max = 0
        coins_min = 0

        for piece in state.board.values():
            if piece == max_label:
                coins_max += 1
            elif piece == min_label:
                coins_min += 1

        total = coins_max + coins_min
        if total > 0:
            return float(100.0 * (coins_max - coins_min) / total)
        return 0.0
