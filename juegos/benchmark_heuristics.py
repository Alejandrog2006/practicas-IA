"""Benchmark competitivo de las heuristicas de Reversi."""

from __future__ import annotations

import argparse
import random
import time
from collections import defaultdict

from game import Player, TwoPlayerGameState, TwoPlayerMatch
from heuristic import Heuristic
from reversi import Reversi
from reversi import create_standard_board
from strategy import MinimaxAlphaBetaStrategy
from p1_1311_08_perez_gonzalez import (
    Bulin47Heuristic,
    IMSERSOheuristic,
    JeanDelPozoHeuristic,
)


HEURISTICS = (JeanDelPozoHeuristic, IMSERSOheuristic, Bulin47Heuristic)


def build_positions(count, plies, seed, obstacles=False):
    """Create reproducible positions for opening, mid-game and endgame."""
    positions = []
    randomizer = random.Random(seed)
    for position_index in range(count):
        black = Player("position-black", MinimaxAlphaBetaStrategy(
            Heuristic("position", lambda state: 0), 1))
        white = Player("position-white", MinimaxAlphaBetaStrategy(
            Heuristic("position", lambda state: 0), 1))
        game = Reversi(black, white, height=8, width=8)
        state = TwoPlayerGameState(
            game=game,
            initial_player=black,
            board=create_standard_board(8, 8, "B", "W"),
        ).setup_match()
        target_plies = plies * (position_index + 1)
        for _ in range(target_plies):
            successors = game.generate_successors(state)
            if not successors:
                break
            state = randomizer.choice(successors)
        board = dict(state.board)
        if obstacles:
            for square in ((1, 1), (8, 2), (1, 7), (7, 8)):
                board.setdefault(square, "O")
        positions.append(board)
    return positions


def build_official_positions():
    """Return the two initial boards used by the course tournament."""
    standard = create_standard_board(8, 8, "B", "W")
    obstacle_board = dict(standard)
    for square in ((2, 1), (8, 2), (1, 7), (7, 8)):
        obstacle_board[square] = "O"
    return [standard, obstacle_board]


def play_game(
    first_class, second_class, depth, board, first_starts=True,
    max_seconds_per_move=30,
):
    first_heuristic = first_class()
    second_heuristic = second_class()
    first = Player(
        first_class.__name__,
        MinimaxAlphaBetaStrategy(
            Heuristic(first_heuristic.get_name(), first_heuristic.evaluation_function),
            max_depth_minimax=depth,
            max_sec_per_evaluation=0,
        ),
    )
    second = Player(
        second_class.__name__,
        MinimaxAlphaBetaStrategy(
            Heuristic(second_heuristic.get_name(), second_heuristic.evaluation_function),
            max_depth_minimax=depth,
            max_sec_per_evaluation=0,
        ),
    )
    game = Reversi(first, second, height=8, width=8)
    state = TwoPlayerGameState(
        game=game,
        initial_player=first if first_starts else second,
        board=dict(board),
    )
    started = time.perf_counter()
    scores = TwoPlayerMatch(
        state,
        n_moves_max=200,
        max_seconds_per_move=max_seconds_per_move,
    ).play_match()
    elapsed = time.perf_counter() - started
    if scores is None:
        raise RuntimeError("La partida no devolvio puntuaciones")
    return scores, elapsed


def run_benchmark(
    depth, positions_count=4, plies=4, seed=131108, alternate_colors=True,
    obstacles=False, official=True, max_seconds_per_move=30, max_games=None,
):
    if depth != 4:
        raise ValueError("Este benchmark debe ejecutarse siempre con depth=4")

    records = []
    totals = defaultdict(lambda: {"wins": 0, "draws": 0, "losses": 0, "points": 0})

    positions = (
        build_official_positions()
        if official
        else build_positions(positions_count, plies, seed, obstacles)
    )
    games_played = 0
    total_games = len(positions) * 6
    for position_index, board in enumerate(positions, start=1):
        for first_class in HEURISTICS:
            for second_class in HEURISTICS:
                if first_class is second_class:
                    continue
                if max_games is not None and games_played >= max_games:
                    break
                first_name = first_class().get_name()
                second_name = second_class().get_name()
                print(
                    f"[{games_played + 1}/{total_games}] "
                    f"P{position_index} {first_name} vs {second_name}...",
                    flush=True,
                )
                first_starts = (
                    (position_index + len(records)) % 2 == 0
                    if alternate_colors
                    else True
                )
                scores, elapsed = play_game(
                    first_class, second_class, depth, board, first_starts,
                    max_seconds_per_move,
                )
                first_score, second_score = map(float, scores)

                if first_score > second_score:
                    result = "win"
                    totals[first_name]["wins"] += 1
                    totals[second_name]["losses"] += 1
                    totals[first_name]["points"] += 3
                elif first_score < second_score:
                    result = "loss"
                    totals[first_name]["losses"] += 1
                    totals[second_name]["wins"] += 1
                    totals[second_name]["points"] += 3
                else:
                    result = "draw"
                    totals[first_name]["draws"] += 1
                    totals[second_name]["draws"] += 1
                    totals[first_name]["points"] += 1
                    totals[second_name]["points"] += 1

                records.append(
                    (position_index, first_name, second_name,
                     first_score, second_score, result, elapsed)
                )
                games_played += 1
            if max_games is not None and games_played >= max_games:
                break
        if max_games is not None and games_played >= max_games:
            break

    print(
        f"\nProfundidad minimax: {depth} | "
        f"Partidas ejecutadas: {games_played}/{total_games}"
    )
    print("\nPartidas:")
    for position, first, second, first_score, second_score, result, elapsed in records:
        print(
            f"P{position} {first:24} vs {second:28} "
            f"{first_score:5.0f}-{second_score:5.0f} "
            f"{result:4} ({elapsed:.2f}s)"
        )

    print("\nClasificacion:")
    ranking = sorted(
        totals.items(),
        key=lambda item: (item[1]["points"], item[1]["wins"]),
        reverse=True,
    )
    for position, (name, values) in enumerate(ranking, start=1):
        print(
            f"{position}. {name:24} "
            f"{values['points']} puntos | "
            f"{values['wins']}V {values['draws']}E {values['losses']}D"
        )

    best_heuristic = HEURISTICS[0]
    best_name = best_heuristic().get_name()
    best_position = next(
        position for position, (name, _) in enumerate(ranking, start=1)
        if name == best_name
    )
    print(
        f"\n{best_heuristic.__name__}: puesto {best_position}/{len(ranking)} "
        f"({totals[best_name]['points']} puntos)"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--depth", type=int, default=4)
    parser.add_argument("--positions", type=int, default=4)
    parser.add_argument("--plies", type=int, default=4)
    parser.add_argument("--seed", type=int, default=131108)
    parser.add_argument("--no-alternate-colors", action="store_true")
    parser.add_argument("--obstacles", action="store_true")
    parser.add_argument("--max-seconds-per-move", type=float, default=30)
    parser.add_argument(
        "--max-games",
        type=int,
        default=None,
        help="Stop after this many games; useful for a quick depth-4 smoke test",
    )
    parser.add_argument(
        "--random-positions",
        action="store_true",
        help="Use generated mid-game positions instead of official starts",
    )
    args = parser.parse_args()
    run_benchmark(
        args.depth,
        args.positions,
        args.plies,
        args.seed,
        not args.no_alternate_colors,
        args.obstacles,
        not args.random_positions,
        args.max_seconds_per_move,
        args.max_games,
    )
