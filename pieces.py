import numpy as np

"""
colour:
    1: white
    0: black
"""

class Pawn:
    def __init__(self, colour, direction):
        self.colour = colour
        self.direction = direction
        self.moved = False

class Rook:
    def __init__(self, colour):
        self.colour = colour

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

class PieceEngine:
    @classmethod
    def in_check(cls, colour, board):
        for y, row in enumerate(board):
            for x, piece in enumerate(row):
                if piece and piece.colour == colour and type(piece) == King:
                    king = [x, y]

        if not "king" in locals():
            raise Exception(f"{['Black', 'White'][colour]} king not on board.")

        # knights
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

        # pawn
        x, y = king

        if colour: # put in loop todo
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

            if board[i[1]][i[0]] and type(board[i[1]][i[0]]) == King:
                return True

        # bishop/queen
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

        # rook/queen
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
    def get_moves(cls, piece, square, board, en_passant=[]):
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
        colour = board[y][x].colour
        moves = []

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
                
        return moves