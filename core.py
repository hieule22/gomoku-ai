from enum import Enum
from random import randint
from time import sleep

MAX_DEPTH = 1
BIG_INITIAL_VALUE = 1000000
DIMENSION = 15


class Piece(Enum):
    """A piece on the board can be either empty, black, or white."""
    BLACK = 0
    WHITE = 1
    EMPTY = 2


def get_opponent(player):
    return Piece.BLACK if player == Piece.WHITE else Piece.WHITE


class Player:
    def __init__(self, piece):
        self.piece = piece

    def get_move(self, game):
        return


class RandomPlayer(Player):
    def get_move(self, game):
        moves = game.legal_moves()
        return moves[randint(0, len(moves) - 1)]


class GreedyPlayer(Player):
    def get_move(self, game):
        moves = game.legal_moves()
        result = []
        for move in moves:
            state = game.make_move(move)
            reward = evaluate(state, self)
            result.append((reward, move))
        return max(result)[1]


class AlphaBetaMinimaxPlayer(Player):
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


def evaluate(game, player):
    weights = [2, 200, 2000, 20000]
    reward = 0
    opponent = get_opponent(player)
    for length in range(2, 6):
        reward += weights[length - 2] * get_num_series(game, player, length)
        reward -= weights[length - 2] * get_num_series(game, opponent, length)
    return reward


def play_gomoku(player0, player1):
    # Set-up logic
    players = (player0, player1)
    game = Game(DIMENSION, DIMENSION)

    while True:
        for player in players:
            move = player.get_move(game)
            game = game.make_move(move)
            game.display()

            if game.terminal_test():
                print("Game over")
                return

            sleep(1)


class Game:
    """A game is similar to a problem, but it has a utility for each
    state and a terminal test instead of a path cost and a goal
    test. To create a game, subclass this class and implement
    legal_moves, make_move, utility, and terminal_test. You may
    override display and successors or you can inherit their default
    methods. You will also need to set the .initial attribute to the
    initial state; this can be done in the constructor."""

    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.moves = {}

    def legal_moves(self, distance=1):
        """Return a list of the allowable moves at this point."""
        moves = []
        if len(self.moves) == 0:  # First piece must be at center of the board
            moves.append((self.height // 2, self.width // 2))
        elif len(self.moves) == 1:  # Second piece must be next to first piece.
            center_row, center_col = self.height // 2, self.width // 2
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if not (dr == 0 and dc == 0):
                        moves.append((center_row + dr, center_col + dc))
        else:
            for (row, col) in self.moves:
                for r in range(max(0, row - distance),
                               min(self.height - 1, row + distance) + 1):
                    for c in range(max(0, col - distance),
                                   min(self.width - 1, col + distance) + 1):
                        if self._get_piece(r, c) == Piece.EMPTY:
                            moves.append((r, c))
        return moves

    def make_move(self, move):
        """Return the state that results from making a move from a state."""
        (row, col) = move
        game = Game(self.height, self.width)
        game.moves = self.moves.copy()
        game.moves[(row, col)] = self.to_move()
        return game

    # def utility(self, state, player):
    #     "Return the value of this final state to player."
    #     abstract()

    def terminal_test(self):
        # The game ends in a tie when the board is completely filled.
        if len(self.moves) == self.height * self.width:
            return True

        return (get_num_series(self, Piece.BLACK, 5)
                + get_num_series(self, Piece.WHITE, 5) > 0)

    def to_move(self):
        """Return the player whose move it is in this state."""
        return Piece.BLACK if len(self.moves) % 2 == 0 else Piece.WHITE

    def display(self):
        """Print or otherwise display the state."""
        symbols = ['X', 'O', '.']
        for row in range(self.height):
            for col in range(self.width):
                print(symbols[self._get_piece(row, col).value], end=' ')
            print('\n')
        print('\n')

    def successors(self):
        """Return a list of legal (move, state) pairs."""
        m = [(move, self.make_move(move))
             for move in self.legal_moves()]
        return m

    def is_legal_position(self, row, column):
        """Checks if a specified position is legal"""
        return 0 <= row < self.height and 0 <= column < self.width

    def __repr__(self):
        return '<%s>' % self.__class__.__name__

    def _get_piece(self, row, col):
        return self.moves[(row, col)] if (row, col) in self.moves else Piece.EMPTY

    def check_direction(self, row, column, target_length, direction):
        [dr, dc] = direction
        piece = self._get_piece(row, column)

        # Obtain the maximum chain containing this piece by searching for the
        # position with the maximum/minimum row and column values that has
        # a different piece type than the one being assigned
        min_row, min_column = row - dr, column - dc
        while (self.is_legal_position(min_row, min_column) and
               self._get_piece(min_row, min_column) == piece):
            min_row -= dr
            min_column -= dc
        max_row, max_column = row + dr, column + dc
        while (self.is_legal_position(max_row, max_column) and
               self._get_piece(max_row, max_column) == piece):
            max_row += dr
            max_column += dc

        # Get the length of the resulting streak. The chain length is equal to
        # the difference in row values or in column values.
        length = (abs(max_row - min_row) - 1 if dr != 0
                  else abs(max_column - min_column) - 1)

        if length != target_length:
            return False

        # Winning chain can border the board boundary
        if (not self.is_legal_position(min_row, min_column) or
                not self.is_legal_position(max_row, max_column)):
            return True

        # Winning chain must not be surrounded by two pieces of opposite type
        return (self._get_piece(min_row, min_column) == Piece.EMPTY or
                self._get_piece(max_row, max_column) == Piece.EMPTY)


game_cache = {}


def get_num_series(game, player, length):
    if (game, player, length) in game_cache:
        return game_cache[(game, player, length)]

    num_series = 0
    directions = [[1, 0], [0, 1], [1, 1], [1, -1]]
    for (row, col) in game.moves:
        if game.moves[(row, col)] == player:
            for direction in directions:
                if game.check_direction(row, col, length, direction):
                    num_series += 1

    num_series /= length
    game_cache[(game, player, length)] = num_series
    return num_series


# play_gomoku(GreedyPlayer(Piece.BLACK), AlphaBetaMinimaxPlayer(Piece.WHITE))
