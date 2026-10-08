import unittest

from game import Player, TwoPlayerGameState
from reversi import Reversi
from strategy import RandomStrategy
from p1_1311_08_perez_gonzalez import (
    ChampionHeuristic,
    Solution2,
    Solution3,
)


def make_state(board, max_player="B"):
    player1 = Player("Black", RandomStrategy())
    player2 = Player("White", RandomStrategy())
    player1.label = "B"
    player2.label = "W"
    game = Reversi(player1, player2, height=8, width=8)
    player_max = player1 if max_player == "B" else player2
    return TwoPlayerGameState(
        game=game,
        initial_player=player1,
        player_max=player_max,
        board=board,
    )


class ChampionHeuristicTest(unittest.TestCase):
    def test_api_and_initial_position(self):
        heuristic = ChampionHeuristic()
        state = make_state({
            (4, 4): "W",
            (5, 5): "W",
            (4, 5): "B",
            (5, 4): "B",
        })

        self.assertEqual(heuristic.get_name(), "1311_08_champion")
        self.assertIsInstance(heuristic.evaluation_function(state), float)

    def test_uses_player_max_perspective(self):
        board = {(2, 2): "B", (3, 3): "W"}
        value_for_black = ChampionHeuristic().evaluation_function(
            make_state(board, max_player="B")
        )
        value_for_white = ChampionHeuristic().evaluation_function(
            make_state(board, max_player="W")
        )

        self.assertEqual(value_for_black, -value_for_white)
        self.assertLess(value_for_black, 0)

    def test_final_phase_uses_piece_difference(self):
        board = {}
        for index, position in enumerate(
            (x, y) for y in range(1, 9) for x in range(1, 9)
        ):
            board[position] = "B" if index < 40 else "W"

        value = ChampionHeuristic().evaluation_function(make_state(board))

        self.assertEqual(value, 1600.0)

    def test_terminal_result_dominates_positional_score(self):
        state = make_state({(1, 1): "W", (2, 2): "B"})
        state.end_of_game = True
        state.scores = [20, 40]

        self.assertEqual(
            ChampionHeuristic().evaluation_function(state),
            -10020.0,
        )


class OtherHeuristicsTest(unittest.TestCase):
    def test_all_heuristics_have_tournament_api(self):
        state = make_state({(1, 1): "B", (8, 8): "W"})
        heuristics = (ChampionHeuristic(), Solution2(), Solution3())

        for heuristic in heuristics:
            with self.subTest(heuristic=heuristic.__class__.__name__):
                self.assertIsInstance(heuristic.get_name(), str)
                self.assertIsInstance(
                    heuristic.evaluation_function(state),
                    float,
                )

    def test_solution2_and_solution3_use_max_perspective_at_terminal_state(self):
        state = make_state({(1, 1): "B", (8, 8): "W"}, max_player="W")
        state.end_of_game = True
        state.scores = [10, 6]

        expected = -10004.0
        self.assertEqual(Solution2().evaluation_function(state), expected)
        self.assertEqual(Solution3().evaluation_function(state), expected)


if __name__ == "__main__":
    unittest.main()
