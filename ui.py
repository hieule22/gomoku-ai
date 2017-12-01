from core import Game as Game
from core import Player as Player
from core import Piece as Piece

from tkinter import *

MARGIN = 20  # Pixels around the board
SIDE = 25  # Width of every board cell.
WIDTH = HEIGHT = MARGIN * 2 + SIDE * 15  # Width and height of the whole board

Bord = [["-" for x in range(15)] for y in range(15)]


class GomokuUI(Frame):
    """
    The Tkinter UI, responsible for drawing the board and accepting user input.
    """

    def __init__(self, parent):
        self.game = Game(15, 15)
        self.players = (Player(), Player())
        Frame.__init__(self, parent)
        self.parent = parent

        self.row, self.col = -1, -1

        self.__initUI()

    def __initUI(self):
        self.parent.title("Gomoku")
        self.pack(fill=BOTH)
        self.canvas = Canvas(self,
                             width=WIDTH,
                             height=HEIGHT)
        self.canvas.pack(fill=BOTH, side=TOP)
        advance_button = Button(self,
                                text="Next Move",
                                command=self.__start_game)
        advance_button.pack(fill=BOTH, side=BOTTOM)

        self.__draw_grid()
        self.__draw_puzzle()

    def __draw_grid(self):
        """
        Draws grid divided with blue lines into 3x3 squares
        """
        for i in range(18):
            color = "blue"

            x0 = MARGIN + i * SIDE
            y0 = MARGIN
            x1 = MARGIN + i * SIDE
            y1 = HEIGHT - MARGIN
            self.canvas.create_line(x0, y0, x1, y1, fill=color)

            x0 = MARGIN
            y0 = MARGIN + i * SIDE
            x1 = WIDTH - MARGIN
            y1 = MARGIN + i * SIDE
            self.canvas.create_line(x0, y0, x1, y1, fill=color)

    def __draw_puzzle(self):
        self.canvas.delete("numbers")
        icons = ['X', 'O', 'z']
        for i in range(15):
            for j in range(15):
                answer = self.game.cells[i][j]
                if answer != Piece.EMPTY:
                    x = MARGIN + j * SIDE + SIDE / 2
                    y = MARGIN + i * SIDE + SIDE / 2
                    color = "black" if answer == Piece.BLACK else "sea green"
                    self.canvas.create_text(
                        x, y, text=icons[answer.value], tags="numbers", fill=color
                    )

    def __draw_cursor(self):
        self.canvas.delete("cursor")
        if self.row >= 0 and self.col >= 0:
            x0 = MARGIN + self.col * SIDE + 1
            y0 = MARGIN + self.row * SIDE + 1
            x1 = MARGIN + (self.col + 1) * SIDE - 1
            y1 = MARGIN + (self.row + 1) * SIDE - 1
            self.canvas.create_rectangle(
                x0, y0, x1, y1,
                outline="red", tags="cursor"
            )

    def __start_game(self):
        if self.game.terminal_test():
            return

        player = self.players[0] if self.game.to_move() == Piece.BLACK else self.players[1]
        move = player.random_search(self.game)
        self.game.make_move(move)
        self.__draw_grid()
        self.__draw_puzzle()
        self.__draw_cursor()


if __name__ == '__main__':
    root = Tk()
    ui = GomokuUI(root)
    root.geometry("%dx%d" % (WIDTH, HEIGHT + 40))
    root.mainloop()
