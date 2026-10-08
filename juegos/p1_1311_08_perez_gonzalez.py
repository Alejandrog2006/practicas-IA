"""
Funciones heuristicas para el torneo
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

# Matriz estatica de ponderacion posicional para Reversi 8x8.
BASE_WEIGHTS = (
    (120, -60, 15, 10, 10, 15, -60, 120),
    (-60, -25, -5, -5, -5, -5, -25, -60),
    (15, -5, 5, 2, 2, 5, -5, 15),
    (10, -5, 2, 1, 1, 2, -5, 10),
    (10, -5, 2, 1, 1, 2, -5, 10),
    (15, -5, 5, 2, 2, 5, -5, 15),
    (-60, -25, -5, -5, -5, -5, -25, -60),
    (120, -60, 15, 10, 10, 15, -60, 120),
)


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


class ChampionHeuristic(StudentHeuristic):
    """
    Heuristica posicional con ajuste de esquinas y penalizacion de frontera.
    """

    def get_name(self) -> str:
        return "1311_08_champion"

    def evaluation_function(self, state: TwoPlayerGameState) -> float:
        is_term, term_val = _eval_terminal(state)
        if is_term:
            return term_val

        max_label = state.player_max.label
        min_label = (
            state.player2.label
            if state.player1.label == max_label
            else state.player1.label
        )
        pieces = state.board
        weights = [list(row) for row in BASE_WEIGHTS]

        corners = ((1, 1), (1, 8), (8, 1), (8, 8))
        for corner_x, corner_y in corners:
            corner_piece = pieces.get((corner_x, corner_y))
            if corner_piece in (max_label, min_label):
                for x, y in (
                    (corner_x + (1 if corner_x == 1 else -1), corner_y),
                    (corner_x, corner_y + (1 if corner_y == 1 else -1)),
                    (
                        corner_x + (1 if corner_x == 1 else -1),
                        corner_y + (1 if corner_y == 1 else -1),
                    ),
                ):
                    weights[y - 1][x - 1] = 15

        my_pieces = 0
        opponent_pieces = 0
        my_frontier = 0
        opponent_frontier = 0
        pos_score = 0.0

        for (x, y), piece in pieces.items():
            if piece == 'O':
                continue
            if piece != max_label and piece != min_label:
                continue

            if piece == max_label:
                my_pieces += 1
                sign = 1.0
            else:
                opponent_pieces += 1
                sign = -1.0

            pos_score += sign * weights[y - 1][x - 1]

            is_frontier = any(
                1 <= x + dx <= 8
                and 1 <= y + dy <= 8
                and (x + dx, y + dy) not in pieces
                for dx in (-1, 0, 1)
                for dy in (-1, 0, 1)
                if dx != 0 or dy != 0
            )
            if is_frontier:
                if piece == max_label:
                    my_frontier += 1
                else:
                    opponent_frontier += 1

        total_pieces = my_pieces + opponent_pieces
        if total_pieces > 50:
            return float((my_pieces - opponent_pieces) * 100.0)

        frontier_score = -(my_frontier - opponent_frontier) * 8.0
        return float(pos_score + frontier_score)


class Solution2(StudentHeuristic):
    """
    Se basa en la estabilidad de las piezas: las esquinas
    son inalterables una vez se colocan, y los bordes ofrecen anclajes defensivos.
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
    """
    Evalua la diferencia porcentual entre el numero de fichas propias
    y del contrario.
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
