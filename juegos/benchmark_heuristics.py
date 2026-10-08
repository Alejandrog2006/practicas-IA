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
    ChampionHeuristic,
    Solution2,
    Solution3,
)


HEURISTICS = (ChampionHeuristic, Solution2, Solution3)


def build_positions(count, plies, seed):
    """Create reproducible mid-game positions without changing heuristics."""
    positions = [create_standard_board(8, 8, "B", "W")]
    randomizer = random.Random(seed)
    for position_index in range(1, count):
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
        for _ in range(plies * position_index):
            successors = game.generate_successors(state)
            if not successors:
                break
            state = randomizer.choice(successors)
        positions.append(dict(state.board))
    return positions


def play_game(first_class, second_class, depth, board):
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
        initial_player=first,
        board=dict(board),
    )
    started = time.perf_counter()
    scores = TwoPlayerMatch(
        state,
        n_moves_max=200,
        max_seconds_per_move=30,
    ).play_match()
    elapsed = time.perf_counter() - started
    if scores is None:
        raise RuntimeError("La partida no devolvio puntuaciones")
    return scores, elapsed


def run_benchmark(depth, positions_count=1, plies=8, seed=131108):
    records = []
    totals = defaultdict(lambda: {"wins": 0, "draws": 0, "losses": 0, "points": 0})

    positions = build_positions(positions_count, plies, seed)
    for position_index, board in enumerate(positions, start=1):
        for first_class in HEURISTICS:
            for second_class in HEURISTICS:
                if first_class is second_class:
                    continue
                scores, elapsed = play_game(first_class, second_class, depth, board)
                first_name = first_class().get_name()
                second_name = second_class().get_name()
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

    print(f"Profundidad minimax: {depth}")
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

    champion = ChampionHeuristic().get_name()
    champion_position = next(
        position for position, (name, _) in enumerate(ranking, start=1)
        if name == champion
    )
    print(
        f"\nChampionHeuristic: puesto {champion_position}/{len(ranking)} "
        f"({totals[champion]['points']} puntos)"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--positions", type=int, default=1)
    parser.add_argument("--plies", type=int, default=8)
    parser.add_argument("--seed", type=int, default=131108)
    args = parser.parse_args()
    run_benchmark(args.depth, args.positions, args.plies, args.seed)
