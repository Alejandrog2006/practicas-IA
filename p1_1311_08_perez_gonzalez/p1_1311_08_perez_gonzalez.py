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


# Matriz estatica de ponderacion posicional para Reversi 8x8
BASE_WEIGHTS = (
    (120, -28,  20,  10,  10,  20, -28, 120),
    (-28, -75,  -6,  -4,  -4,  -6, -75, -28),
    ( 20,  -6,  15,   3,   3,  15,  -6,  20),
    ( 10,  -4,   3,   1,   1,   3,  -4,  10),
    ( 10,  -4,   3,   1,   1,   3,  -4,  10),
    ( 20,  -6,  15,   3,   3,  15,  -6,  20),
    (-28, -75,  -6,  -4,  -4,  -6, -75, -28),
    (120, -28,  20,  10,  10,  20, -28, 120),
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


def _edge_stability(board, max_label, min_label, width=8, height=8):
    """
    Cuenta fichas estables (indestructibles) en los 4 bordes ancladas a una
    esquina ocupada o protegidas directamente por un obstaculo 'O'.
    """
    edge_scans = (
        # Borde superior (izquierda a derecha y derecha a izquierda)
        (1, 1, 1, 0, width), (width, 1, -1, 0, width),
        # Borde inferior
        (1, height, 1, 0, width), (width, height, -1, 0, width),
        # Borde izquierdo
        (1, 1, 0, 1, height), (1, height, 0, -1, height),
        # Borde derecho
        (width, 1, 0, 1, height), (width, height, 0, -1, height),
    )

    stable_coords_max = set()
    stable_coords_min = set()

    for sx, sy, dx, dy, length in edge_scans:
        anchored = False
        curr_owner = None

        for step in range(length):
            cx, cy = sx + step * dx, sy + step * dy
            p = board.get((cx, cy))

            if p == 'O':
                # Un obstaculo bloquea la linea de captura y sirve de ancla
                anchored = True
                curr_owner = None
                continue

            if step == 0 and p in (max_label, min_label):
                # La propia esquina esta ocupada: sirve de ancla inicial
                anchored = True
                curr_owner = p

            if not anchored:
                continue

            if p is None:
                # Se rompe la cadena de estabilidad hasta encontrar otro obstaculo
                anchored = False
                curr_owner = None
                continue

            if curr_owner is None:
                curr_owner = p

            if p == curr_owner:
                if p == max_label:
                    stable_coords_max.add((cx, cy))
                elif p == min_label:
                    stable_coords_min.add((cx, cy))
            else:
                anchored = False
                curr_owner = None

    return len(stable_coords_max), len(stable_coords_min)


def _board_features(board, max_label, min_label, width=8, height=8):
    """
    Calcula rasgos del tablero en una sola pasada O(N) y recolecta
    las casillas vacias adyacentes para acelerar el calculo de movilidad.
    """
    max_pieces = min_pieces = 0
    max_corners = min_corners = 0
    max_safe_edges = min_safe_edges = 0
    max_frontier = min_frontier = 0
    max_danger = min_danger = 0
    positional = 0.0
    empty_candidates = set()

    # Mapa de casillas X (mas graves: factor 2) y casillas C (factor 1)
    x_squares = {
        (2, 2): (1, 1),
        (width - 1, 2): (width, 1),
        (2, height - 1): (1, height),
        (width - 1, height - 1): (width, height),
    }
    c_squares = {
        (1, 2): (1, 1), (2, 1): (1, 1),
        (width - 1, 1): (width, 1), (width, 2): (width, 1),
        (1, height - 1): (1, height), (2, height): (1, height),
        (width - 1, height): (width, height), (width, height - 1): (width, height),
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

        # 1. Esquinas, casillas X, casillas C y bordes
        if x in (1, width) and y in (1, height):
            if sign > 0:
                max_corners += 1
            else:
                min_corners += 1
            weight = 125.0
        elif (x, y) in x_squares:
            assoc_corner = x_squares[(x, y)]
            corner_owner = board.get(assoc_corner)
            if corner_owner is None:
                # Casilla X con esquina vacia: penalizacion doble
                if sign > 0:
                    max_danger += 2
                else:
                    min_danger += 2
                weight = -75.0
            elif corner_owner == piece:
                weight = 18.0
            else:
                weight = -10.0
        elif (x, y) in c_squares:
            assoc_corner = c_squares[(x, y)]
            corner_owner = board.get(assoc_corner)
            if corner_owner is None:
                if sign > 0:
                    max_danger += 1
                else:
                    min_danger += 1
                weight = -28.0
            elif corner_owner == piece:
                weight = 18.0
                if sign > 0:
                    max_safe_edges += 1
                else:
                    min_safe_edges += 1
            else:
                weight = -8.0
        else:
            weight = BASE_WEIGHTS[y - 1][x - 1] if (1 <= x <= 8 and 1 <= y <= 8) else 0.0
            if x in (1, width) or y in (1, height):
                if sign > 0:
                    max_safe_edges += 1
                else:
                    min_safe_edges += 1

        positional += sign * weight

        # 2. Fichas frontera y recoleccion de candidatos vacios para movilidad
        is_frontier = False
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            if 1 <= nx <= width and 1 <= ny <= height and (nx, ny) not in board:
                is_frontier = True
                empty_candidates.add((nx, ny))
        if is_frontier:
            if sign > 0:
                max_frontier += 1
            else:
                min_frontier += 1

    stable_max, stable_min = _edge_stability(board, max_label, min_label, width, height)

    return (
        max_pieces, min_pieces,
        max_corners, min_corners,
        max_safe_edges, min_safe_edges,
        max_frontier, min_frontier,
        max_danger, min_danger,
        stable_max, stable_min,
        positional,
        empty_candidates,
    )


def _mobility_and_corner_threats(board, candidates, max_label, min_label, width, height):
    """
    Calcula en una sola llamada los movimientos legales y cuantas esquinas vacias
    son capturables en el siguiente turno (evitando el efecto horizonte en d+1).
    """
    corners_set = {(1, 1), (width, 1), (1, height), (width, height)}

    def _scan_player(p_label, e_label):
        legal_moves = 0
        capturable_corners = 0
        for x, y in candidates:
            is_legal = False
            for dx, dy in DIRECTIONS:
                nx, ny = x + dx, y + dy
                if board.get((nx, ny)) != e_label:
                    continue
                nx += dx
                ny += dy
                while 1 <= nx <= width and 1 <= ny <= height:
                    cell = board.get((nx, ny))
                    if cell == e_label:
                        nx += dx
                        ny += dy
                    elif cell == p_label:
                        is_legal = True
                        break
                    else:
                        break
                if is_legal:
                    break
            if is_legal:
                legal_moves += 1
                if (x, y) in corners_set:
                    capturable_corners += 1
        return legal_moves, capturable_corners

    moves_max, next_corners_max = _scan_player(max_label, min_label)
    moves_min, next_corners_min = _scan_player(min_label, max_label)
    return moves_max, moves_min, next_corners_max, next_corners_min


class JeanDelPozoHeuristic(StudentHeuristic):
    """
    Heuristica #1: Heurística con perfil de evaporación en apertura y control de movilidad relativa.
    """

    def get_name(self) -> str:
        return "JeanDelPozoHeuristic"

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
            stable_max, stable_min,
            positional,
            candidates,
        ) = _board_features(state.board, max_label, min_label, width, height)

        total = coins_max + coins_min
        if total == 0:
            return 0.0

        if total >= 59:
            return float((coins_max - coins_min) * 150.0 + positional)

        moves_max, moves_min, next_c_max, next_c_min = _mobility_and_corner_threats(
            state.board, candidates, max_label, min_label, width, height
        )
        mob_denom = moves_max + moves_min
        mobility = 100.0 * (moves_max - moves_min) / mob_denom if mob_denom else 0.0

        wipeout_bonus = 0.0
        if moves_min == 0 and moves_max > 0:
            wipeout_bonus = 75.0
        elif moves_max == 0 and moves_min > 0:
            wipeout_bonus = -75.0

        next_label = state.next_player.label if state.next_player else None
        c_threat_max = next_c_max * (85.0 if next_label == max_label else 50.0)
        c_threat_min = next_c_min * (85.0 if next_label == min_label else 50.0)

        parity = 100.0 * (coins_max - coins_min) / total

        if total < 22:
            parity_weight = -0.35
            frontier_weight = 9.5
            mob_weight = 1.55
        elif total < 50:
            parity_weight = 0.40
            frontier_weight = 8.5
            mob_weight = 1.35
        else:
            parity_weight = 4.0
            frontier_weight = 7.5
            mob_weight = 1.25

        return float(
            1.14 * positional
            + mob_weight * mobility
            + wipeout_bonus
            + 94.0 * (corners_max - corners_min)
            + (c_threat_max - c_threat_min)
            + 29.5 * (stable_max - stable_min)
            + 7.8 * (edges_max - edges_min)
            + parity_weight * parity
            - frontier_weight * (frontier_max - frontier_min)
            - 25.5 * (danger_max - danger_min)
        )

class IMSERSOheuristic(StudentHeuristic):
    """
    Heuristica #2: Heurística orientada a estabilidad de bordes con obstáculos y control de paridad.
    """

    def get_name(self) -> str:
        return "IMSERSOheuristic"

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
            stable_max, stable_min,
            positional,
            candidates,
        ) = _board_features(state.board, max_label, min_label, width, height)

        total = pieces_max + pieces_min
        if total == 0:
            return 0.0

        if total >= 59:
            return float((pieces_max - pieces_min) * 150.0 + positional)

        moves_max, moves_min, next_c_max, next_c_min = _mobility_and_corner_threats(
            state.board, candidates, max_label, min_label, width, height
        )
        mob_denom = moves_max + moves_min
        mobility = 100.0 * (moves_max - moves_min) / mob_denom if mob_denom else 0.0

        wipeout_bonus = 0.0
        if moves_min == 0 and moves_max > 0:
            wipeout_bonus = 75.0
        elif moves_max == 0 and moves_min > 0:
            wipeout_bonus = -75.0

        next_label = state.next_player.label if state.next_player else None
        c_threat_max = next_c_max * (85.0 if next_label == max_label else 50.0)
        c_threat_min = next_c_min * (85.0 if next_label == min_label else 50.0)

        parity = 100.0 * (pieces_max - pieces_min) / total

        if total < 22:
            parity_weight = -0.30
            frontier_weight = 9.5
            mob_weight = 1.5
        elif total < 50:
            parity_weight = 0.38
            frontier_weight = 8.2
            mob_weight = 1.35
        else:
            parity_weight = 3.5 + (total - 50) * 0.30
            frontier_weight = 5.5
            mob_weight = 1.10

        return float(
            1.12 * positional
            + mob_weight * mobility
            + wipeout_bonus
            + 92.0 * (corners_max - corners_min)
            + (c_threat_max - c_threat_min)
            + 29.0 * (stable_max - stable_min)
            + 7.5 * (edges_max - edges_min)
            + parity_weight * parity
            - frontier_weight * (frontier_max - frontier_min)
            - 25.0 * (danger_max - danger_min)
        )


class Bulin47Heuristic(StudentHeuristic):
    """
    Heurística #3: Heurística posicional con alta ponderación de esquinas, estabilidad en bordes y ahogo del rival.
    """

    def get_name(self) -> str:
        return "Bulin47Heuristic"

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
            stable_max, stable_min,
            positional,
            candidates,
        ) = _board_features(state.board, max_label, min_label, width, height)

        total = pieces_max + pieces_min
        if total >= 59:
            return float((pieces_max - pieces_min) * 150.0 + positional)

        moves_max, moves_min, next_c_max, next_c_min = _mobility_and_corner_threats(
            state.board, candidates, max_label, min_label, width, height
        )
        mob_denom = moves_max + moves_min
        mobility = 100.0 * (moves_max - moves_min) / mob_denom if mob_denom else 0.0

        wipeout_bonus = 0.0
        if moves_min == 0 and moves_max > 0:
            wipeout_bonus = 75.0
        elif moves_max == 0 and moves_min > 0:
            wipeout_bonus = -75.0

        next_label = state.next_player.label if state.next_player else None
        c_threat_max = next_c_max * (85.0 if next_label == max_label else 50.0)
        c_threat_min = next_c_min * (85.0 if next_label == min_label else 50.0)

        parity = 100.0 * (pieces_max - pieces_min) / total if total else 0.0
        parity_weight = -0.25 if total < 22 else (0.4 if total < 50 else 4.2)

        return float(
            1.15 * positional
            + 1.3 * mobility
            + wipeout_bonus
            + 95.0 * (corners_max - corners_min)
            + (c_threat_max - c_threat_min)
            + 30.0 * (stable_max - stable_min)
            + 8.0 * (edges_max - edges_min)
            + parity_weight * parity
            - 8.5 * (frontier_max - frontier_min)
            - 26.0 * (danger_max - danger_min)
        )