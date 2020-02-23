from pieces import PieceEngine, generate_board
#from graphics import GraphicsEngine
import sys

"""
Engine ids:
    0 - Standard variant

todo:
pgn
timer (+intervals)
add comprehensive algebraic notation (i.e. +/-, ! etc)
more helpful validation messages
"""

class Engine:
    def __init__(self, text=True):
        self.board = generate_board()
        self.turn = True # white

        if text:
            self.print_instructions()
            self.display_board()

        self.en_passant_eligible = [[], []] # white eligible, black eligible

    def move(self, move):
        start, end = move

        start_x = "ABCDEFGH".index(start[0])
        start_y = int(start[1]) - 1

        end_x = "ABCDEFGH".index(end[0])
        end_y = int(end[1]) - 1
        
        piece = self.board[start_y][start_x]

        if not piece or not self.turn == piece.colour:
            return False

        moves = PieceEngine.get_moves(piece, [start_x, start_y], self.board, self.en_passant_eligible)
        
        print(piece, moves)
  
        if not moves or not [end_x, end_y] in moves:
            return False

        if not self.board[end_y][end_x].__class__.__name__ == "King":
            captured = self.board[end_y][end_x]
            self.board[end_y][end_x] = self.board[start_y][start_x]
            self.board[start_y][start_x] = 0
        else:
            return False

        if PieceEngine.in_check(self.turn, self.board):
            self.board[start_y][start_x] = self.board[end_y][end_x]
            self.board[end_y][end_x] = captured
            return False

        # check for pawn promotions

        if piece.__class__.__name__ == "Pawn":
            self.board[end_y][end_x].moved = True

            if abs(start_y - end_y) == 2:
                self.en_passant_eligible[self.turn].append([end_x, end_y])

            if not start_x == end_x:
                self.board[start_y][end_x] = 0

        self.turn = not self.turn
        self.en_passant_eligible[self.turn] = []

        return True

    def print_instructions(self):
        print("""\
Moves should be input in the form:
    [Start Square][End Square]
e.g.
    g1f3

Illegal move inputs will be flagged.
The board will be printed out after every turn.\n""")

    def display_board(self):
        for p, row in enumerate(self.board[::-1]):
            print(8-p, end=" ")

            for piece in row:
                if not piece:
                    print(" ", end=" ")
                else:
                    if not piece.colour:
                        print(piece.__class__.__name__[0].lower() if not piece.__class__.__name__ == "Knight" else "n", end=" ")
                    else:
                        print(piece.__class__.__name__[0] if not piece.__class__.__name__ == "Knight" else "N", end=" ")

            print() # debug

        print(" " + "ABCDEFGH".replace("", " "))

    def pgn(self):
        pass

class Chess: # main handler class
    def __init__(self, engineid=0):
        self._build_engine(engineid)

    def input(self):
        move = input(f"{['Black', 'White'][self.engine.turn]}'s move: ").upper()
        legal, parsed = self._parse_input(move)

        if move == "EXIT":
            sys.exit()

        if not legal:
            return "Invalid move, re-enter."

        resp = self.engine.move(parsed)

        if not resp:
            return "Illegal move, re-enter."
            
        self.engine.display_board()

    def _parse_input(self, move):
        if not len(move) == 4 or move[:2] == move[-2:]:
            return False, None

        letters = [move[0], move[2]]
        nums = [move[1], move[3]]

        if not all(64 < ord(m) < 73 for m in letters):
            return False, None

        if not all(n.isdigit() and 0 < int(n) < 9 for n in nums):
            return False, None

        return True, [move[:2], move[2:]]

    def _build_engine(self, _id):
        if not _id:
            self.engine = Engine()
        else:
            raise Exception("Engine ID not found.")

    def reset(self):
        self.__init__()