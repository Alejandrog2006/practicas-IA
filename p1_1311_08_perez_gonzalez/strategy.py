"""Strategies for two player games.

    Autores:
        Fabiano Baroni <fabiano.baroni@uam.es>,
        Alejandro Bellogin Kouki <alejandro.bellogin@uam.es>
        Alberto Suárez <alberto.suarez@uam.es>
    
        Arturo Perez Noves <arturo.perezn@estudiante.uam.es>
        Alejandro Gonzalez Garcia <alejandro.gonzalez06@estudiante.uam.es>
        
    Grupo: 1311
    Pareja: 08
"""

from __future__ import annotations  # For Python 3.7

from abc import ABC, abstractmethod
import time
from typing import List, Optional, Tuple

import numpy as np

from game import TwoPlayerGame, TwoPlayerGameState
from heuristic import Heuristic


class Strategy(ABC):
    """Abstract base class for player's strategy."""

    def __init__(self, verbose: int = 0) -> None:
        """Initialize common attributes for all derived classes."""
        self.verbose = verbose

    @abstractmethod
    def next_move(
        self,
        state: TwoPlayerGameState,
        gui: bool = False,
    ) -> TwoPlayerGameState:
        """Compute next move."""

    def generate_successors(
        self,
        state: TwoPlayerGameState,
    ) -> List[TwoPlayerGameState]:
        """Generate state successors."""
        assert isinstance(state.game, TwoPlayerGame)
        successors = state.game.generate_successors(state)
        assert successors  # Error if list is empty
        return successors


class RandomStrategy(Strategy):
    """Strategy in which moves are selected uniformly at random."""

    def next_move(
        self,
        state: TwoPlayerGameState,
        gui: bool = False,
    ) -> TwoPlayerGameState:
        """Compute next move."""
        successors = self.generate_successors(state)
        return np.random.choice(successors)


class ManualStrategy(Strategy):
    """Strategy in which the player inputs a move."""

    def next_move(
        self,
        state: TwoPlayerGameState,
        gui: bool = False,
    ) -> TwoPlayerGameState:
        """Compute next move"""
        successors = self.generate_successors(state)

        assert isinstance(state.game, TwoPlayerGame)
        if gui:
            index_successor = state.game.graphical_input(state, successors)
        else:
            index_successor = state.game.manual_input(successors)

        next_state = successors[index_successor]

        if self.verbose > 0:
            print('My move is: {:s}'.format(str(next_state.move_code)))

        return next_state


class MinimaxStrategy(Strategy):
    """Elige movimientos mediante el algoritmo minimax con profundidad limitada.
    La heurística devuelve un valor desde el punto de vista de MAX. Por tanto,
    MAX selecciona el sucesor con mayor valor y MIN el que tiene menor valor.
    La búsqueda alterna entre ambas operaciones hasta alcanzar un estado terminal o la profundidad configurada.
    """

    def __init__(
        self,
        heuristic: Heuristic,
        max_depth_minimax: int,
        max_sec_per_evaluation: float = 0,
        verbose: int = 0,
    ) -> None:
        super().__init__(verbose)
        self.heuristic = heuristic
        self.max_depth_minimax = max_depth_minimax
        self.max_sec_per_evaluation = max_sec_per_evaluation
        self.timed_out = False

    def next_move(
        self,
        state: TwoPlayerGameState,
        gui: bool = False,
    ) -> TwoPlayerGameState:
        """Devuelve el mejor sucesor encontrado desde el estado actual """

        # El jugador actual se trata como MAX en la raíz de la búsqueda
        # Después, las llamadas recursivas alternan entre MAX y MIN
        minimax_value, minimax_successor = self._max_value(
            state,
            self.max_depth_minimax,
        )

        if self.verbose > 0:
            if self.verbose > 1:
                print('\nGame state before move:\n')
                print(state.board)
                print()
            print('Minimax value = {:.2g}'.format(minimax_value))

        return minimax_successor

    def _min_value(
        self,
        state: TwoPlayerGameState,
        depth: int,
    ) -> float:
        """Devuelve el valor suponiendo que el siguiente jugador es MIN"""

        # en una hoja no hay movimiento que elegir: se evalúa el tablero
        if state.end_of_game or depth == 0:
            if self.timed_out:
                minimax_value = 0
            else:
                time0 = time.time()
                minimax_value = self.heuristic.evaluate(state)
                time1 = time.time()
                timediff = time1 - time0
                if (self.max_sec_per_evaluation > 0) and (timediff > self.max_sec_per_evaluation):
                    print("Heuristic {} timeout: {} > {}".format(self.heuristic.get_name(), timediff, self.max_sec_per_evaluation))
                    self.timed_out = True
            minimax_successor = None
        else:
            minimax_value = np.inf

            # MIN supone que el oponente elige el sucesor peor para MAX
            for successor in self.generate_successors(state):
                if self.verbose > 1:
                    print('{}: {}'.format(state.board, minimax_value))

                successor_minimax_value, _ = self._max_value(
                    successor,
                    depth - 1,
                )

                if (successor_minimax_value < minimax_value):
                    minimax_value = successor_minimax_value
                    minimax_successor = successor

        if self.verbose > 1:
            print('{}: {}'.format(state.board, minimax_value))

        return minimax_value, minimax_successor

    def _max_value(
        self,
        state: TwoPlayerGameState,
        depth: int,
    ) -> float:
        """Devuelve el valor suponiendo que el siguiente jugador es MAX"""

        # un estado terminal o el límite de profundidad termina esta rama
        if state.end_of_game or depth == 0:
            if self.timed_out:
                minimax_value = 0
            else:
                time0 = time.time()
                minimax_value = self.heuristic.evaluate(state)
                time1 = time.time()
                timediff = time1 - time0
                if (self.max_sec_per_evaluation > 0) and (timediff > self.max_sec_per_evaluation):
                    print("Heuristic {} timeout: {} > {}".format(self.heuristic.get_name(), timediff, self.max_sec_per_evaluation))
                    self.timed_out = True
            minimax_successor = None
        else:
            minimax_value = -np.inf

            # MAX supone que el jugador elige el sucesor mejor para MAX
            for successor in self.generate_successors(state):
                if self.verbose > 1:
                    print('{}: {}'.format(state.board, minimax_value))

                successor_minimax_value, _ = self._min_value(
                    successor,
                    depth - 1,
                )
                if (successor_minimax_value > minimax_value):
                    minimax_value = successor_minimax_value
                    minimax_successor = successor

        if self.verbose > 1:
            print('{}: {}'.format(state.board, minimax_value))

        return minimax_value, minimax_successor


class MinimaxAlphaBetaStrategy(Strategy):
    """Estrategia minimax acelerada mediante poda alfa-beta.
    Calcula el mismo resultado que MinimaxStrategy pero evita
    explorar ramas que no pueden mejorar la decisión encontrada. Alpha
    es el mejor valor garantizado para MAX y beta es el mejor valor
    garantizado para MIN a lo largo del camino actual
    """

    def __init__(
        self,
        heuristic: Heuristic,
        max_depth_minimax: int,
        max_sec_per_evaluation: float = 0,
        verbose: int = 0,
    ) -> None:
        super().__init__(verbose)
        self.heuristic = heuristic
        self.max_depth_minimax = max_depth_minimax
        self.max_sec_per_evaluation = max_sec_per_evaluation
        self.timed_out = False

    def next_move(
        self,
        state: TwoPlayerGameState,
        gui: bool = False,
    ) -> TwoPlayerGameState:
        """Devuelve el mejor sucesor encontrado usando poda alfa-beta"""

        # Al principio ningún jugador tiene una cota, por lo que el intervalo no está acotado
        minimax_value, minimax_successor = self._max_value(
            state,
            self.max_depth_minimax,
            alpha=-np.inf,
            beta=np.inf,
        )

        if self.verbose > 0:
            if self.verbose > 1:
                print('\nGame state before move:\n')
                print(state.board)
                print()
            print('Minimax value = {:.2g}'.format(minimax_value))

        return minimax_successor

    def _min_value(
        self,
        state: TwoPlayerGameState,
        depth: int,
        alpha: float,
        beta: float,
    ) -> Tuple[float, Optional[TwoPlayerGameState]]:
        """Evalúa un nodo MIN y poda sucesores que no pueden influir."""

        # la evaluación de una hoja es igual que en el minimax normal
        if state.end_of_game or depth == 0:
            if self.timed_out:
                minimax_value = 0
            else:
                time0 = time.time()
                minimax_value = self.heuristic.evaluate(state)
                time1 = time.time()
                timediff = time1 - time0
                if (self.max_sec_per_evaluation > 0) and (timediff > self.max_sec_per_evaluation):
                    print("Heuristic {} timeout: {} > {}".format(self.heuristic.get_name(), timediff, self.max_sec_per_evaluation))
                    self.timed_out = True
            minimax_successor = None
        else:
            minimax_value = np.inf
            minimax_successor = None

            # Paso MIN: seleccionar la cota inferior para el adversario
            for successor in self.generate_successors(state):
                if self.verbose > 1:
                    print('{}: [{:.2g}, {:.2g}]'.format(
                            state.board,
                            alpha,
                            beta,
                        )
                    )

                successor_minimax_value, _ = self._max_value(
                    successor,
                    depth - 1,
                    alpha,
                    beta,
                )

                if minimax_successor is None or successor_minimax_value < minimax_value:
                    minimax_value = successor_minimax_value
                    minimax_successor = successor

                # Poda alfa: el nodo no puede empeorar la mejor opción de MAX
                if minimax_value <= alpha:
                    break

                # MIN mejora su cota superior tras examinar este hijo
                beta = min(beta, minimax_value)

        if self.verbose > 1:
            print('{}: [{:.2g}, {:.2g}]'.format(
                    state.board,
                    alpha,
                    beta,
                )
            )

        return minimax_value, minimax_successor

    def _max_value(
        self,
        state: TwoPlayerGameState,
        depth: int,
        alpha: float,
        beta: float,
    ) -> Tuple[float, Optional[TwoPlayerGameState]]:
        """Evalúa un nodo MAX y poda sucesores que no pueden influir."""

        # La evaluación de una hoja es igual que en el minimax normal
        if state.end_of_game or depth == 0:
            if self.timed_out:
                minimax_value = 0
            else:
                time0 = time.time()
                minimax_value = self.heuristic.evaluate(state)
                time1 = time.time()
                timediff = time1 - time0
                if (self.max_sec_per_evaluation > 0) and (timediff > self.max_sec_per_evaluation):
                    print("Heuristic {} timeout: {} > {}".format(self.heuristic.get_name(), timediff, self.max_sec_per_evaluation))
                    self.timed_out = True
            minimax_successor = None
        else:
            minimax_value = -np.inf
            minimax_successor = None

            # Paso MAX: seleccionar el valor más favorable
            for successor in self.generate_successors(state):
                if self.verbose > 1:
                    print('{}: [{:.2g}, {:.2g}]'.format(
                            state.board,
                            alpha,
                            beta,
                        )
                    )

                successor_minimax_value, _ = self._min_value(
                    successor,
                    depth - 1,
                    alpha,
                    beta,
                )

                if minimax_successor is None or successor_minimax_value > minimax_value:
                    minimax_value = successor_minimax_value
                    minimax_successor = successor

                # Poda beta: el nodo no puede superar la cota de MIN
                if minimax_value >= beta:
                    break

                # MAX mejora su cota inferior tras examinar este hijo
                alpha = max(alpha, minimax_value)

        if self.verbose > 1:
            print('{}: [{:.2g}, {:.2g}]'.format(
                    state.board,
                    alpha,
                    beta,
                )
            )

        return minimax_value, minimax_successor
