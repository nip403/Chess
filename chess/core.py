import numpy as np
import sys

"""
Engine ids:
    0 - Standard variant

"""

"fix castling!!!!!!!!!!!!!!!!!!!!!!"

# todo:
#   castling
#   pgn
#   timer (+intervals)
#   add comprehensive algebraic notation (i.e. +/-, ! etc)
#   more helpful validation messages
#   add comments for piece/move logic

# piece objects
class Pawn:
    def __init__(self, colour, direction):
        self.colour = colour
        self.direction = direction
        self.moved = False

class Rook:
    def __init__(self, colour):
        self.colour = colour
        self.moved = False

class Bishop:
    def __init__(self, colour):
        self.colour = colour

class Knight:
    def __init__(self, colour):
        self.colour = colour

class Queen:
    def __init__(self, colour):
        self.colour = colour

class King:
    def __init__(self, colour):
        self.colour = colour
        self.moved = False

class Engine:
    meta = "Chess"

    def __init__(self, text=True):
        self.board = generate_board()
        self.turn = True # white = 1, black = 0

        if text:
            self.print_instructions()
            self.display_board()

        self.en_passant_eligible = [[], []] # white eligible, black eligible

    def move(self, move, handle):
        start, end = move

        # convert to array indices
        start_x = "ABCDEFGH".index(start[0])
        start_y = int(start[1]) - 1

        end_x = "ABCDEFGH".index(end[0])
        end_y = int(end[1]) - 1
        
        piece = self.board[start_y][start_x]

        # validate piece and turn
        if not piece or not self.turn == piece.colour:
            return False

        # get available moves
        moves = PieceEngine.get_moves(piece, [start_x, start_y], self.board, self.en_passant_eligible)

        # castling
        if type(piece) == King:
            moves, castle_moves = moves

            if [end_x, end_y] in castle_moves:
                self.board[end_y][end_x] = piece
                self.board[start_y][start_x] = 0

                if end_x < start_x:
                    self.board[end_y][0].moved = True
                    self.board[end_y][end_x+1] = self.board[end_y][0]
                    self.board[end_y][0] = 0
                else:
                    self.board[end_y][-1].moved = True
                    self.board[end_y][end_x-1] = self.board[end_y][-1]
                    self.board[end_y][-1] = 0

                piece.moved = True
                self.turn = not self.turn

                return True

        # check if piece can move to selected dest
        if not moves or not [end_x, end_y] in moves:
            return False

        # ensure king is not captured
        if not type(self.board[end_y][end_x]) == King:
            captured = self.board[end_y][end_x] # placeholder for piece taken if new game state is check
            self.board[end_y][end_x] = self.board[start_y][start_x] # move
            self.board[start_y][start_x] = 0
        else:
            return False

        # prevent castling after moved
        if type(piece) in [King, Rook]:
            piece.moved = True

        # if new position is in check for move's own colour
        if PieceEngine.in_check(self.turn, self.board):
            self.board[start_y][start_x] = self.board[end_y][end_x] # swap back
            self.board[end_y][end_x] = captured
            return False

        if type(piece) == Pawn:
            # check for en passant
            self.board[end_y][end_x].moved = True

            if abs(start_y - end_y) == 2:
                self.en_passant_eligible[self.turn].append([end_x, end_y])

            if not start_x == end_x:
                self.board[start_y][end_x] = 0

            # check for pawn promotion
            if (end_y == 7 and piece.colour) or (not end_y and not piece.colour):
                choice = handle._promotion_choice()
                self.board[end_y][end_x] = {
                    "Q": Queen(piece.colour),
                    "R": Rook(piece.colour),
                    "B": Bishop(piece.colour),
                    "K": Knight(piece.colour),
                }[choice]

        self.turn = not self.turn
        self.en_passant_eligible[self.turn] = [] # clear en passant

        return True

    def checkmate(self):
        pass

    def stalemate(self):
        pass

    def print_instructions(self):
        print("""\
Moves should be input in the form:
    [Start Square][End Square]
e.g.
    g1f3

Illegal/invalid move inputs will be flagged.
The board will be printed out after every turn.\n""")

    def display_board(self):
        for p, row in enumerate(self.board if not self.turn else self.board[::-1]):
            print(8-p if self.turn else p+1, end=" ")

            for piece in row:
                if not piece:
                    print(" ", end=" ")
                else:
                    if not piece.colour:
                        print(piece.__class__.__name__[0].lower() if not type(piece) == Knight else "n", end=" ")
                    else:
                        print(piece.__class__.__name__[0] if not type(piece) == Knight else "N", end=" ")

            print() 

        print(" " + "ABCDEFGH".replace("", " "))

def generate_board(): # from white's perspective as index 0 = white
    return [ # Cols ABCDEFGH, Rows 12345678 (from index 0-8)
        [Rook(1), Knight(1), Bishop(1), Queen(1), King(1), Bishop(1), Knight(1), Rook(1)],
        [Pawn(1, 1) for _ in range(8)],
        [0]*8,
        [0]*8,
        [0]*8,
        [0]*8,
        [Pawn(0, -1) for _ in range(8)],
        [Rook(0), Knight(0), Bishop(0), Queen(0), King(0), Bishop(0), Knight(0), Rook(0)],
    ]

# logic for finding moves & calculating check
class PieceEngine:
    @classmethod
    def in_check(cls, colour, board, king=None):
        if king is None:
            del king

            # find position of correct king
            for y, row in enumerate(board):
                for x, piece in enumerate(row):
                    if piece and piece.colour == colour and type(piece) == King:
                        king = [x, y]

            # check for existence of king
            if not "king" in locals():
                raise Exception(f"{['Black', 'White'][colour]} king not on board.")

        else:
            assert all(isinstance(i, int) and 0 <= i < 8 for i in king), "Invalid square."

        # knight checks
        x, y = king

        for i in [
            [x+1, y+2],
            [x-1, y+2],
            [x+1, y-2],
            [x-1, y-2],
            [x+2, y+1],
            [x+2, y-1],
            [x-2, y+1],
            [x-2, y-1],
        ]:
            if any(not 0 <= j < 8 for j in i):
                continue

            piece = board[i[1]][i[0]]

            if piece and not piece.colour == colour and type(piece) == Knight:
                return True

        # pawn checks
        x, y = king

        if colour:
            for t in [-1, 1]: 
                if x + t < 8 and y < 7 and board[y+1][x+t] and not board[y+1][x+t].colour and type(board[y+1][x+t]) == Pawn:
                    return True
        else:
            for t in [-1, 1]: 
                if x + t < 8 and y > 0 and board[y-1][x+t] and board[y-1][x+t].colour and type(board[y-1][x+t]) == Pawn:
                    return True

        # if next to king
        x, y = king

        for i in [
            [x-1, y-1],
            [x, y-1],
            [x+1, y-1],
            [x-1, y],
            [x+1, y],
            [x-1, y+1],
            [x, y+1],
            [x+1, y+1],
        ]:
            if not all(0 <= j < 8 for j in i):
                continue

            if board[i[1]][i[0]] and type(board[i[1]][i[0]]) == King and not board[i[1]][i[0]].colour == colour:
                return True

        # bishop/queen checks
        x, y = king

        while True:
            x += 1
            y += 1

            if x > 7 or y > 7:
                break
            
            if board[y][x]:
                if not board[y][x].colour == colour and type(board[y][x]) in [Bishop, Queen]:
                    return True

                break

        x, y = king

        while True:
            x += 1
            y -= 1

            if x > 7 or y < 0:
                break
                
            if board[y][x]:
                if not board[y][x].colour == colour and type(board[y][x]) in [Bishop, Queen]:
                    return True

                break

        x, y = king

        while True:
            x -= 1
            y += 1

            if x < 0 or y > 7:
                break

            if board[y][x]:
                if not board[y][x].colour == colour and type(board[y][x]) in [Bishop, Queen]:
                    return True

                break

        x, y = king

        while True:
            x -= 1
            y -= 1

            if x < 0 or y < 0:
                break

            if board[y][x]:
                if not board[y][x].colour == colour and type(board[y][x]) in [Bishop, Queen]:
                    return True

                break

        # rook/queen checks
        x, y = king
        transpose = list(map(list, zip(*board)))

        for i in range(x+1, 8):
            if board[y][i]:
                if not board[y][i].colour == colour and type(board[y][i]) in [Rook, Queen]:
                    return True

                break

        for i in reversed(range(x)):
            if board[y][i]:
                if not board[y][i].colour == colour and type(board[y][i]) in [Rook, Queen]:
                    return True

                break

        for i in range(y+1, 8):
            if transpose[x][i]:
                if not transpose[x][i].colour == colour and type(transpose[x][i]) in [Rook, Queen]:
                    return True7

                break

        for i in reversed(range(y)):
            if transpose[x][i]:
                if not transpose[x][i].colour == colour and type(transpose[x][i]) in [Rook, Queen]:
                    return True

                break
        
        return False
        
    @classmethod
    def get_moves(cls, piece, square, board, en_passant=[[], []]):
        if type(piece) == Rook:
            return cls.get_rook_moves(square, board)

        elif type(piece) == Bishop:
            return cls.get_bishop_moves(square, board)

        elif type(piece) == Knight:
            return cls.get_knight_moves(square, board)

        elif type(piece) == Queen:
            return cls.get_queen_moves(square, board)

        elif type(piece) == Pawn:
            return cls.get_pawn_moves(square, board, en_passant)

        elif type(piece) == King:
            return cls.get_king_moves(square, board)

        return False

    @classmethod
    def get_rook_moves(cls, square, board):
        x, y = square
        colour = board[y][x].colour
        transpose = list(map(list, zip(*board)))
        moves = []

        for i in range(x+1, 8):
            if board[y][i]:
                if not board[y][i].colour == colour:
                    moves.append([i, y])

                break

            moves.append([i, y])

        for i in reversed(range(x)):
            if board[y][i]:
                if not board[y][i].colour == colour:
                    moves.append([i, y])

                break

            moves.append([i, y])

        for i in range(y+1, 8):
            if transpose[x][i]:
                if not transpose[x][i].colour == colour:
                    moves.append([x, i])

                break

            moves.append([x, i])

        for i in reversed(range(y)):
            if transpose[x][i]:
                if not transpose[x][i].colour == colour:
                    moves.append([x, i])

                break

            moves.append([x, i])

        return moves

    @classmethod
    def get_bishop_moves(cls, square, board):
        x, y = square
        colour = board[y][x].colour
        moves = []

        while True:
            x += 1
            y += 1

            if x > 7 or y > 7:
                break
            
            if board[y][x]:
                if not board[y][x].colour == colour:
                    moves.append([x, y])

                break

            moves.append([x, y])

        x, y = square

        while True:
            x += 1
            y -= 1

            if x > 7 or y < 0:
                break
                
            if board[y][x]:
                if not board[y][x].colour == colour:
                    moves.append([x, y])

                break

            moves.append([x, y])

        x, y = square

        while True:
            x -= 1
            y += 1

            if x < 0 or y > 7:
                break

            if board[y][x]:
                if not board[y][x].colour == colour:
                    moves.append([x, y])

                break

            moves.append([x, y])

        x, y = square

        while True:
            x -= 1
            y -= 1

            if x < 0 or y < 0:
                break

            if board[y][x]:
                if not board[y][x].colour == colour:
                    moves.append([x, y])

                break

            moves.append([x, y])

        return moves

    @classmethod
    def get_knight_moves(cls, square, board):
        x, y = square
        colour = board[y][x].colour
        moves = []

        for i in [
            [x+1, y+2],
            [x-1, y+2],
            [x+1, y-2],
            [x-1, y-2],
            [x+2, y+1],
            [x+2, y-1],
            [x-2, y+1],
            [x-2, y-1],
        ]:
            if any(not 0 <= j < 8 for j in i):
                continue

            if board[i[1]][i[0]] and board[i[1]][i[0]].colour == colour:
                continue

            moves.append(i)

        return moves

    @classmethod
    def get_queen_moves(cls, square, board):
        return cls.get_bishop_moves(square, board) + cls.get_rook_moves(square, board)

    @classmethod
    def get_pawn_moves(cls, square, board, en_passant):
        x, y = square
        piece = board[y][x]
        colour = piece.colour
        moves = []

        if not board[y + piece.direction][x]:
            moves.append([x, y + piece.direction])
        
        if not piece.moved and not board[y + (2*piece.direction)][x]:
            moves.append([x, y + (2*piece.direction)])

        if x > 0 and board[y + piece.direction][x-1] and not board[y + piece.direction][x-1].colour == colour:
            moves.append([x-1, y + piece.direction])

        if x < 7 and board[y + piece.direction][x+1] and not board[y + piece.direction][x+1].colour == colour:
            moves.append([x+1, y + piece.direction])

        # en passant
        if x < 7:
            right = board[y][x+1]

            if right and type(right) == Pawn and not right.colour == colour and [x+1, y] in en_passant[right.colour]:
                if (y == 4 and colour) or (y == 3 and not colour):
                    moves.append([x+1, y + piece.direction])

        if x > 0:
            left = board[y][x-1]

            if left and type(left) == Pawn and not left.colour == colour and [x-1, y] in en_passant[left.colour]:
                if (y == 4 and colour) or (y == 3 and not colour):
                    
                    moves.append([x-1, y + piece.direction])

        return moves

    @classmethod
    def get_king_moves(cls, square, board):
        x, y = square
        piece = board[y][x]
        colour = piece.colour
        moves = []
        castle_moves = []

        # standard logic
        for i in [
            [x-1, y-1],
            [x, y-1],
            [x+1, y-1],
            [x-1, y],
            [x+1, y],
            [x-1, y+1],
            [x, y+1],
            [x+1, y+1],
        ]:
            if not 0 <= i[0] < 8 or not 0 <= i[1] < 8:
                continue

            if not board[i[1]][i[0]] or not board[i[1]][i[0]].colour == colour:
                moves.append(i)

        # castling logic
        if not piece.moved:

            # left
            x_left = x
            can_castle_left = True

            while x_left > 2:
                x_left -= 1

                if board[y][x_left] or cls.in_check(colour, board, [x_left, y]):
                    can_castle_left = False
                    break

            if can_castle_left:
                p_left = board[y][0]
                
                if p_left and type(p_left) == Rook and p_left.colour == colour:
                    castle_moves.append([x_left, y])

            # right
            x_right = x
            can_castle_right = True

            while x_right < 6:
                x_right += 1

                if board[y][x_right] or cls.in_check(colour, board, [x_right, y]):
                    can_castle_right = False
                    break

            if can_castle_right:
                p_right = board[y][-1]

                if p_right and type(p_right) == Rook and p_right.colour == colour:
                    castle_moves.append([x_right, y])

        return moves, castle_moves
