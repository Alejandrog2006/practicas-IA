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


# Matriz estatica corregida: X-squares (-65) mas penalizadas que C-squares (-25)
BASE_WEIGHTS = (
    (120, -25,  20,  10,  10,  20, -25, 120),
    (-25, -65,  -5,  -5,  -5,  -5, -65, -25),
    ( 20,  -5,  15,   3,   3,  15,  -5,  20),
    ( 10,  -5,   3,   1,   1,   3,  -5,  10),
    ( 10,  -5,   3,   1,   1,   3,  -5,  10),
    ( 20,  -5,  15,   3,   3,  15,  -5,  20),
    (-25, -65,  -5,  -5,  -5,  -5, -65, -25),
    (120, -25,  20,  10,  10,  20, -25, 120),
)

DIRECTIONS = (
    (-1, -1), (-1, 0), (-1, 1), (0, -1),
    (0, 1), (1, -1), (1, 0), (1, 1),
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


def _board_features(board, max_label, min_label, width=8, height=8):
    """
    Calcula rasgos del tablero en una sola pasada en O(N),
    incluyendo ajuste dinamico de casillas X/C cuando la esquina esta ocupada.
    """
    max_pieces = min_pieces = 0
    max_corners = min_corners = 0
    max_safe_edges = min_safe_edges = 0
    max_frontier = min_frontier = 0
    max_danger = min_danger = 0
    positional = 0.0

    # Mapa rapido de casillas X/C asociadas a su esquina
    corner_map = {
        (1, 2): (1, 1), (2, 1): (1, 1), (2, 2): (1, 1),
        (width - 1, 1): (width, 1), (width, 2): (width, 1), (width - 1, 2): (width, 1),
        (1, height - 1): (1, height), (2, height): (1, height), (2, height - 1): (1, height),
        (width - 1, height): (width, height), (width, height - 1): (width, height), (width - 1, height - 1): (width, height),
    }

    for (x, y), piece in board.items():
        if piece == max_label:
            sign = 1
            max_pieces += 1
        elif piece == min_label:
            sign = -1
            min_pieces += 1
        else:
            # Ignorar obstaculos 'O'
            continue

        # 1. Esquinas, bordes seguros y casillas peligrosas (X/C)
        if x in (1, width) and y in (1, height):
            if sign > 0:
                max_corners += 1
            else:
                min_corners += 1
            weight = 120.0
        elif (x, y) in corner_map:
            assoc_corner = corner_map[(x, y)]
            corner_owner = board.get(assoc_corner)
            # Si la esquina sigue libre, es una casilla muy peligrosa
            if corner_owner is None:
                if sign > 0:
                    max_danger += 1
                else:
                    min_danger += 1
                weight = BASE_WEIGHTS[y - 1][x - 1] if (1 <= x <= 8 and 1 <= y <= 8) else -40.0
            elif corner_owner == piece:
                # Si la esquina ya es nuestra, la casilla adyacente es estable y positiva
                weight = 15.0
                if x in (1, width) or y in (1, height):
                    if sign > 0:
                        max_safe_edges += 1
                    else:
                        min_safe_edges += 1
            else:
                weight = -5.0
        else:
            weight = BASE_WEIGHTS[y - 1][x - 1] if (1 <= x <= 8 and 1 <= y <= 8) else 0.0
            if x in (1, width) or y in (1, height):
                if sign > 0:
                    max_safe_edges += 1
                else:
                    min_safe_edges += 1

        positional += sign * weight

        # 2. Fichas frontera (adyacentes a al menos una casilla vacia)
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            if 1 <= nx <= width and 1 <= ny <= height and (nx, ny) not in board:
                if sign > 0:
                    max_frontier += 1
                else:
                    min_frontier += 1
                break

    return (
        max_pieces, min_pieces,
        max_corners, min_corners,
        max_safe_edges, min_safe_edges,
        max_frontier, min_frontier,
        max_danger, min_danger,
        positional,
    )


def _legal_move_count(board, player_label, enemy_label, width, height):
    """Cuenta movimientos legales sin invocar ninguna funcion del motor."""
    candidates = set()
    for x, y in board:
        for dx, dy in DIRECTIONS:
            move = (x + dx, y + dy)
            if (
                1 <= move[0] <= width
                and 1 <= move[1] <= height
                and move not in board
            ):
                candidates.add(move)

    legal_moves = 0
    for x, y in candidates:
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            enemy_seen = False
            while (
                1 <= nx <= width
                and 1 <= ny <= height
                and board.get((nx, ny)) == enemy_label
            ):
                enemy_seen = True
                nx += dx
                ny += dy
            if enemy_seen and board.get((nx, ny)) == player_label:
                legal_moves += 1
                break
    return legal_moves


def _mobility(board, max_label, min_label, width, height):
    """Devuelve la movilidad de ambos jugadores desde el tablero."""
    return (
        _legal_move_count(board, max_label, min_label, width, height),
        _legal_move_count(board, min_label, max_label, width, height),
    )


class JoeBidenHeuristic(StudentHeuristic):
    """
    Heuristica hibrida completa: combina matriz posicional dinamica,
    movilidad real controlada, penalizacion de frontera y transicion al endgame.
    """

    def get_name(self) -> str:
        return "JoeBidenHeuristic"

    def evaluation_function(self, state: TwoPlayerGameState) -> float:
        is_term, term_val = _eval_terminal(state)
        if is_term:
            return term_val

        max_label, min_label = _get_player_labels(state)
        width = getattr(state.game, "width", 8)
        height = getattr(state.game, "height", 8)
        (
            pieces_max, pieces_min,
            corners_max, corners_min,
            edges_max, edges_min,
            frontier_max, frontier_min,
            danger_max, danger_min,
            positional,
        ) = _board_features(state.board, max_label, min_label, width, height)

        total = pieces_max + pieces_min

        # Fase final: el conteo de fichas es la señal dominante y estable.
        if total > 52:
            return float((pieces_max - pieces_min) * 100.0)

        moves_max, moves_min = _mobility(
            state.board, max_label, min_label, width, height
        )
        mob_denom = moves_max + moves_min
        mobility = 100.0 * (moves_max - moves_min) / mob_denom if mob_denom else 0.0

        # Escala equilibrada: 100% de movilidad vale ~150-200 pts, nunca mas que regalar una esquina
        phase = 0 if total < 24 else 1
        mob_weight = (1.8, 1.2)[phase]
        pos_weight = (1.0, 1.3)[phase]

        return float(
            pos_weight * positional
            + mob_weight * mobility
            + 80.0 * (corners_max - corners_min)
            + 8.0 * (edges_max - edges_min)
            - 8.0 * (frontier_max - frontier_min)
            - 25.0 * (danger_max - danger_min)
        )


class EinsteinyTesla(StudentHeuristic):
    """
    Heuristica ultrarrapida O(N) (sin llamadas a _get_valid_moves):
    Maximiza estabilidad en esquinas y bordes seguros, usando la frontera
    como aproximacion instantanea de la movilidad pasiva. Imune a timeouts.
    """

    def get_name(self) -> str:
        return "EinsteinyTesla"

    def evaluation_function(self, state: TwoPlayerGameState) -> float:
        is_term, term_val = _eval_terminal(state)
        if is_term:
            return term_val

        max_label, min_label = _get_player_labels(state)
        width = getattr(state.game, "width", 8)
        height = getattr(state.game, "height", 8)
        (
            pieces_max, pieces_min,
            corners_max, corners_min,
            edges_max, edges_min,
            frontier_max, frontier_min,
            danger_max, danger_min,
            positional,
        ) = _board_features(state.board, max_label, min_label, width, height)

        total = pieces_max + pieces_min
        if total > 52:
            return float((pieces_max - pieces_min) * 80.0)

        return float(
            positional
            + 60.0 * (corners_max - corners_min)
            + 10.0 * (edges_max - edges_min)
            - 10.0 * (frontier_max - frontier_min)
            - 20.0 * (danger_max - danger_min)
        )


class FarmeoAura(StudentHeuristic):
    """
    Heuristica progresiva por fases (Apertura, Medio Juego, Final):
    Pondera la paridad de fichas de forma adaptativa sin descuidar la
    proteccion de esquinas ni las casillas X/C.
    """

    def get_name(self) -> str:
        return "FarmeoAura"

    def evaluation_function(self, state: TwoPlayerGameState) -> float:
        is_term, term_val = _eval_terminal(state)
        if is_term:
            return term_val

        max_label, min_label = _get_player_labels(state)
        width = getattr(state.game, "width", 8)
        height = getattr(state.game, "height", 8)
        (
            coins_max, coins_min,
            corners_max, corners_min,
            edges_max, edges_min,
            frontier_max, frontier_min,
            danger_max, danger_min,
            positional,
        ) = _board_features(state.board, max_label, min_label, width, height)

        total = coins_max + coins_min
        if total == 0:
            return 0.0

        parity = 100.0 * (coins_max - coins_min) / total

        # En apertura penalizamos comer demasiadas fichas; en el final lo premiamos fuerte
        if total < 22:
            parity_weight = -0.3
            frontier_weight = 12.0
        elif total < 48:
            parity_weight = 0.4
            frontier_weight = 8.0
        else:
            parity_weight = 4.5
            frontier_weight = 2.0

        return float(
            positional
            + 70.0 * (corners_max - corners_min)
            + 6.0 * (edges_max - edges_min)
            + parity_weight * parity
            - frontier_weight * (frontier_max - frontier_min)
            - 25.0 * (danger_max - danger_min)
        )