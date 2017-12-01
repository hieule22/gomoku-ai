"""Different modes of playing agent for Gomoku game"""

from core import *
from random import randint


class GomokuPlayer:
    """Base interface for defining a Gomoku-playing agent"""

    def __init__(self, piece):
        """Constructs an agent that plays a given piece"""
        self.piece = piece

    def get_move(self, game):
        """
        Overrides this method to specify the next move for a given game state
        """
        return


class RandomPlayer(GomokuPlayer):
    """A player that randomly chooses the next move"""

    def get_move(self, game):
        moves = game.legal_moves()
        return moves[randint(0, len(moves) - 1)]


def evaluate(game, player):
    """Evaluates the desirability of a given board state for a given player"""
    weights = [2, 200, 2000, 20000]
    reward = 0
    opponent = get_opponent(player)
    for length in range(2, 6):
        reward += weights[length - 2] * get_num_series(game, player, length)
        reward -= weights[length - 2] * get_num_series(game, opponent, length)
    return reward


class GreedyPlayer(GomokuPlayer):
    """
    A player that greedily chooses the move that maximizes the desirability
    of the next immediate game state
    """

    def get_move(self, game):
        moves = game.legal_moves()
        result = []
        for move in moves:
            state = game.make_move(move)
            reward = evaluate(state, self)
            result.append((reward, move))
        return max(result)[1]


class AlphaBetaMinimaxPlayer(GomokuPlayer):
    """
    A player that uses depth-limited minimax player with alpha-beta pruning to
    determine the next optimal move
    """

    def get_move(self, game):
        def max_value(game, alpha, beta, depth):
            if game.terminal_test() or depth > MAX_DEPTH:
                return evaluate(game, self.piece)
            value = -BIG_INITIAL_VALUE
            for (action, state) in game.successors():
                value = max(value, min_value(state, alpha, beta, depth + 1))
                if value >= beta:
                    return value
                alpha = max(alpha, value)
            return value

        def min_value(game, alpha, beta, depth):
            if game.terminal_test() or depth > MAX_DEPTH:
                return evaluate(game, self.piece)
            value = BIG_INITIAL_VALUE
            for (action, state) in game.successors():
                value = min(value, max_value(state, alpha, beta, depth + 1))
                if value <= alpha:
                    return value
                beta = min(beta, value)
            return value

        best_value = -BIG_INITIAL_VALUE
        best_action = None
        for (action, state) in game.successors():
            value = min_value(state, -BIG_INITIAL_VALUE, BIG_INITIAL_VALUE, 0)
            if best_value < value:
                best_value, best_action = value, action

        return best_action
