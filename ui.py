from core import *

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
        self.players = (GreedyPlayer(Piece.BLACK),
                        GreedyPlayer(Piece.WHITE))
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
                                command=self.__advance_game)
        advance_button.pack(fill=BOTH, side=BOTTOM)

        self.__draw_grid()
        self.__draw_puzzle()

    def __draw_grid(self):
        """
        Draws grid divided with blue lines into 3x3 squares
        """
        for i in range(18):
            color = "black"

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
                answer = self.game._get_piece(i, j)
                if answer != Piece.EMPTY:
                    x = MARGIN + j * SIDE + SIDE / 2
                    y = MARGIN + i * SIDE + SIDE / 2
                    color = "black" if answer == Piece.BLACK else "purple"
                    self.canvas.create_text(
                        x, y, text=icons[answer.value], tags="numbers", fill=color
                    )

    def __draw_victory(self, winner):
        x0 = y0 = MARGIN + SIDE * 3
        x1 = y1 = MARGIN + SIDE * 12
        self.canvas.create_oval(
            x0, y0, x1, y1,
            tags="victory", fill="purple", outline="black"
        )
        # create text
        x = y = MARGIN + 7.1 * SIDE + SIDE / 2.8
        self.canvas.create_text(
            x, y,
            text="Player " + str(winner) + " wins!", tags="victory",
            fill="white", font=("Arial", 28)
        )

    def __advance_game(self):
        if self.game.terminal_test():
            self.__draw_victory(2 if self.game.to_move() == Piece.BLACK else 1)
            return

        player = self.players[0] if self.game.to_move() == Piece.BLACK else self.players[1]
        move = player.get_move(self.game)
        self.game = self.game.make_move(move)
        self.game.display()
        self.__draw_grid()
        self.__draw_puzzle()


if __name__ == '__main__':
    root = Tk()
    ui = GomokuUI(root)
    root.geometry("%dx%d" % (WIDTH, HEIGHT + 40))
    root.mainloop()
