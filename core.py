"""
This class defines the representation of the game state and the operations that
could be performed on the state.
"""

from enum import Enum
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
    """Returns the opponent of the given player"""
    return Piece.BLACK if player == Piece.WHITE else Piece.WHITE


def play_gomoku(player0, player1):
    """Plays a Gomoku game on the command-line"""
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
    def __init__(self, height, width):
        """Constructs a blank game state with the given dimensions"""
        self.height = height
        self.width = width
        self.moves = {}

    def legal_moves(self, distance=1):
        """Return a list of the allowable moves at this point"""
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
                        if self.get_piece(r, c) == Piece.EMPTY:
                            moves.append((r, c))
        return moves

    def make_move(self, move):
        """Return the state that results from making a move from this state"""
        (row, col) = move
        game = Game(self.height, self.width)
        game.moves = self.moves.copy()
        game.moves[(row, col)] = self.to_move()
        return game

    def terminal_test(self):
        # The game ends in a tie when the board is completely filled.
        if len(self.moves) == self.height * self.width:
            return True

        return (get_num_series(self, Piece.BLACK, 5)
                + get_num_series(self, Piece.WHITE, 5) > 0)

    def to_move(self):
        """Returns the player whose move it is in this state"""
        return Piece.BLACK if len(self.moves) % 2 == 0 else Piece.WHITE

    def display(self):
        """Prints or otherwise display the state"""
        symbols = ['X', 'O', '.']
        for row in range(self.height):
            for col in range(self.width):
                print(symbols[self.get_piece(row, col).value], end=' ')
            print('\n')
        print('\n')

    def successors(self):
        """Returns a list of legal (move, state) pairs"""
        return [(move, self.make_move(move)) for move in self.legal_moves()]

    def is_legal_position(self, row, column):
        """Checks if a specified position is legal"""
        return 0 <= row < self.height and 0 <= column < self.width

    def __repr__(self):
        return '<%s>' % self.__class__.__name__

    def get_piece(self, row, col):
        return self.moves[(row, col)] if (row, col) in self.moves else Piece.EMPTY

    def check_direction(self, row, column, target_length, direction):
        [dr, dc] = direction
        piece = self.get_piece(row, column)

        # Obtain the maximum chain containing this piece by searching for the
        # position with the maximum/minimum row and column values that has
        # a different piece type than the one being assigned
        min_row, min_column = row - dr, column - dc
        while (self.is_legal_position(min_row, min_column) and
               self.get_piece(min_row, min_column) == piece):
            min_row -= dr
            min_column -= dc
        max_row, max_column = row + dr, column + dc
        while (self.is_legal_position(max_row, max_column) and
               self.get_piece(max_row, max_column) == piece):
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
        return (self.get_piece(min_row, min_column) == Piece.EMPTY or
                self.get_piece(max_row, max_column) == Piece.EMPTY)


# Cache to store previously evaluated game states.
game_cache = {}


def get_num_series(game, player, length):
    """
    Get the number of chains of a given length with pieces belonging to a
    given player in a given game state
    """
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

# Comment the following line to allow playing the game on a terminal
# play_gomoku(GreedyPlayer(Piece.BLACK), AlphaBetaMinimaxPlayer(Piece.WHITE))
