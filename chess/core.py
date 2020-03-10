import numpy as np
import sys

"""
Engine ids:
    0 - Standard variant
"""

class Engine:
    meta = "Chess" # Standard variant engine

    def __init__(self):
        self.board = generate_board()
        self.turn = True # white = 1, black = 0    

        self.en_passant_eligible = [[], []] # white eligible, black eligible
        self.halfmove = 0
        self.fullmove = 0
        self.fens = {} # for threefold repetition

    def get_moves(self, square, piece=None):
        if piece is None:
            piece = self.board[square[1]][square[0]]

        moves = PieceEngine.get_moves(piece, square, self.board, self.en_passant_eligible)

        return moves, []

    def move(self, move, handle):
        # N.B. return values from this function goes as follows:
            # False (invalid/illegal move), error_msg
            # True, additional_pgn_info

        start, end = move
        halfmove_updated = False

        # convert to array indices
        start_x = "ABCDEFGH".index(start[0])
        start_y = int(start[1]) - 1

        end_x = "ABCDEFGH".index(end[0])
        end_y = int(end[1]) - 1
        
        piece = self.board[start_y][start_x]

        # validate piece
        if not piece:
            return False, "Empty square."

        # validate turn
        if not self.turn == piece.colour:
            return False, "Piece has incorrect colour."

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
                self._new_turn()
                self.fens = {} # threefold repetition cleared after castle

                return True, "O-O" if piece.colour and start_x == 4 else "O-O-O"

        elif type(piece) == Pawn:
            moves, ep_moves = moves

        # check if piece can move to selected dest
        if not moves or not [end_x, end_y] in moves:
            return False, f"{piece.__class__.__name__} cannot move to {move[-2:][-1]}."

        # ensure king is not captured
        if not type(self.board[end_y][end_x]) == King: # perform move
            captured = self.board[end_y][end_x] # placeholder for piece taken if new game state is check
            self.board[end_y][end_x] = self.board[start_y][start_x]
            self.board[start_y][start_x] = 0

            if not halfmove_updated:
                halfmove_updated = True
                old_halfmove = self.halfmove

                if not captured or not type(self.board[end_y][end_x]) == Pawn:
                    self.halfmove += 1
                else:
                    self.halfmove = 0
        else:
            return False, "Cannot capture king."

        # prevent castling after moved
        if type(piece) in [King, Rook]:
            piece.moved = True

        # if new position is in check for move's own colour
        if PieceEngine.in_check(self.turn, self.board):
            self.board[start_y][start_x] = self.board[end_y][end_x] # swap back
            self.board[end_y][end_x] = captured

            if halfmove_updated:
                self.halfmove = old_halfmove

            return False, "Destination square will result in check."

        elif captured:
            self.fens = {} # threefold repetition cleared after succesful capture

        if type(piece) == Pawn:

            # update en passant eligibility
            self.board[end_y][end_x].moved = True
            self.fens = {} # threefold repetition cleared after en passant

            if abs(start_y - end_y) == 2:
                self.en_passant_eligible[self.turn].append([end_x, end_y])

            # perform en_passant
            if not start_x == end_x and [end_x, end_y] in ep_moves:
                captured_ep = self.board[start_y][end_x] 
                self.board[start_y][end_x] = 0

                if PieceEngine.in_check(self.turn, self.board): # check if capturing en passant exposes discovery check
                    self.board[start_y][start_x] = self.board[end_y][end_x]
                    self.board[start_y][end_x] = captured_ep

                    return False, "En passant results in check."

                self._new_turn()
                
                return True, "e.p."

            # check for pawn promotion
            if (end_y == 7 and piece.colour) or (not end_y and not piece.colour):
                choice = handle._promotion_choice()
                self._new_turn()

                self.board[end_y][end_x] = {
                    "Q": Queen(piece.colour),
                    "R": Rook(piece.colour),
                    "B": Bishop(piece.colour),
                    "K": Knight(piece.colour),
                }[choice]

                self.fens = {} # threefold repetition cleared after promotion

                return True, "=" + choice

        self._new_turn(handle if not type(piece) == Pawn else None) # if pawn moves board cannot be repeated

        return True, ""

    def build_from_localpgn(self, pgn): # add threefold repetition
        self.__init__()

        for i in pgn:
            # check for castling
            if "-" in i:
                i = i.split("-")
                y = int(not self.turn) * 7 # white at index 0
                king = self.board[y][4]
                king.moved = True

                if len(i) == 3: # queenside
                    self.board[y][2] = king
                    self.board[y][3] = self.board[y][0]
                    self.board[y][4] = 0
                    self.board[y][0] = 0
                    self.board[y][3].moved = True

                else: # kingside
                    self.board[y][6] = king
                    self.board[y][5] = self.board[y][-1]
                    self.board[y][4] = 0
                    self.board[y][-1] = 0
                    self.board[y][5].moved = True
                    
            start_x = "ABCDEFGH".index(i[0])
            start_y = int(i[1]) - 1

            end_x = "ABCDEFGH".index(i[2])
            end_y = int(i[3]) - 1

            # perform move
            piece = self.board[start_y][start_x]
            captured = self.board[end_y][end_x]
            self.board[end_y][end_x] = piece
            self.board[start_y][start_x] = 0

             # check for en passant
            if "e.p." in i:
                self.board[end_x][start_y] = 0

            # update en passant
            if type(self.board[end_y][end_x]) == Pawn and abs(start_y - end_y) == 2:
                self.en_passant_eligible[self.turn].append([end_x, end_y])
                piece.moved = True
                self.halfmove = 0
            else:
                if captured:
                    self.halfmove = 0
                else:
                    self.halfmove += 1
                
            if type(piece) == Rook:
                piece.moved = True

            # check for promotion
            if "=" in i:
                self.board[end_y][end_x] = {
                    "Q": Queen(self.board[end_y][end_x].colour),
                    "R": Rook(self.board[end_y][end_x].colour),
                    "B": Bishop(self.board[end_y][end_x].colour),
                    "K": Knight(self.board[end_y][end_x].colour),
                }[i[-1]]

            self._new_turn()

    def stalemate(self):
        white = []
        black = []

        if self.halfmove >= 50:
            return True

        if any(count >= 3 for count in self.fens.values()):
            return True

        # ases of stalemate (e.g. king and king, king w/ bishop/knight and king, etc.)
        for y, row in enumerate(self.board):
            for x, piece in enumerate(row):
                if not piece:
                    continue

                (white if piece.colour else black).append(piece.__class__.__name__[0] if not type(piece) == Knight else "N")

                # checks if a piece is able to move
                if PieceEngine.get_moves(piece, [x, y], self.board, self.en_passant_eligible):
                    return False

        if any(i in white + black for i in "QR"):
            return False

        if len(white + black) == 2: # 2 kings on board
            return True

        # N.B. it is not possible to checkmate if one side has 2 bishops of the same colour, but that is not factored into this
        for s in [[white, black], [black, white]]:
            if len(s[0]) == 1 and len(s[1]) == 2 and "N" in s[1] or "B" in s[1]:
                return True

        return False

    def checkmate(self):
        # if king is not in check in the first place
        if not PieceEngine.in_check(self.turn, self.board):
            return False

        pieces = {
            # piece: [[x, y], [movelist]]
        }

        # get a list of all possible moves
        for y, row in enumerate(self.board):
            for x, piece in enumerate(row):
                if piece and piece.colour == self.turn:
                    moves = PieceEngine.get_moves(piece, [x, y], self.board, self.en_passant_eligible)

                    # filter out empty castle moves for king
                    if type(piece) == King:
                        moves = moves[0]

                    # skip piece if they are unable to move and defend from check
                    if not len(moves):
                        continue

                    pieces[piece] = [[x, y], moves]

        for piece, data in pieces.items():
            pos, moves = data

            for m in moves:

                # perform move
                captured = self.board[m[1]][m[0]]
                self.board[m[1]][m[0]] = self.board[pos[1]][pos[0]]
                self.board[pos[1]][pos[0]] = 0

                check = PieceEngine.in_check(self.turn, self.board)
                
                # undo move
                self.board[pos[1]][pos[0]] = self.board[m[1]][m[0]]
                self.board[m[1]][m[0]] = captured

                if not check: 
                    return False

        # check cannot been evaded

        return True

    def _new_turn(self, handle=None):
        if not self.turn:
            self.fullmove += 1

        self.turn = not self.turn
        self.en_passant_eligible[self.turn] = [] # clear en passant for pawns after one full turn

        if handle is not None:
            if handle.fenboard()[:-1] in self.fens.keys():
                self.fens[handle.fenboard()[:-1]] += 1 # update threefold repetition counter
            else:
                self.fens[handle.fenboard()[:-1]] = 1

def generate_board():
    return [ # white at index 0
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
        if king is None: # by default
            del king

            # find position of correct king
            for y, row in enumerate(board):
                for x, piece in enumerate(row):
                    if piece and piece.colour == colour and type(piece) == King:
                        king = [x, y]

            # check for existence of king
            if not "king" in locals():
                raise Exception(f"{['Black', 'White'][colour]} king not on board.")

        else: # when checking for castling squares; validation
            assert all(isinstance(i, int) and 0 <= i < 8 for i in king), "Invalid square."

        ####                CHECKS FROM KNIGHT              ####

        x, y = king

        # possible relative knight moves
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
            # bound check
            if any(not 0 <= j < 8 for j in i):
                continue

            piece = board[i[1]][i[0]]

            # checks if knight of opponent is checking
            if piece and not piece.colour == colour and type(piece) == Knight:
                return True

        ####                CHECKS FROM PAWN                ####

        x, y = king

        if colour: # white pawns
            for t in [-1, 1]: # left and right
                if x + t < 8 and y < 7 and board[y+1][x+t] and not board[y+1][x+t].colour and type(board[y+1][x+t]) == Pawn:
                    return True

        else: # black pawns
            for t in [-1, 1]: # left and right
                if x + t < 8 and y > 0 and board[y-1][x+t] and board[y-1][x+t].colour and type(board[y-1][x+t]) == Pawn:
                    return True

        ####                NEXT TO OPPONENT'S KING             ####

        x, y = king

        # possible relative king moves
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
            # bound check
            if not all(0 <= j < 8 for j in i):
                continue

            # checks if king is next to another king
            # colour check is necessary when checking for castling availability
            if board[i[1]][i[0]] and type(board[i[1]][i[0]]) == King and not board[i[1]][i[0]].colour == colour:
                return True

        ####                CHECKS FROM BISHOP/QUEEN              ####

        # north east diagonal
        x, y = king

        while True:
            x += 1
            y += 1

            # bound check
            if x > 7 or y > 7:
                break
            
            if board[y][x]:
                # checks if bishop/queen of opponent is checking
                # does not register check if piece is not an opponent bishop/queen, and breaks as line of check is broken
                if not board[y][x].colour == colour and type(board[y][x]) in [Bishop, Queen]:
                    return True

                break

         # south east diagonal
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

        # north west diagonal
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

        # south west diagonal
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

        ####                CHECKS FROM ROOK/QUEEN              ####

        x, y = king
        transpose = list(map(list, zip(*board))) # for ease of checking columns

        # right
        for i in range(x+1, 8):
            if board[y][i]:
               # checks if rook/queen of opponent is checking
                # does not register check if piece is not an opponent rook/queen, and breaks as line of check is broken
                if not board[y][i].colour == colour and type(board[y][i]) in [Rook, Queen]:
                    return True

                break

        # left
        for i in reversed(range(x)):
            if board[y][i]:
                if not board[y][i].colour == colour and type(board[y][i]) in [Rook, Queen]:
                    return True

                break

        # up
        for i in range(y+1, 8):
            if transpose[x][i]:
                if not transpose[x][i].colour == colour and type(transpose[x][i]) in [Rook, Queen]:
                    return True

                break

        # down
        for i in reversed(range(y)):
            if transpose[x][i]:
                if not transpose[x][i].colour == colour and type(transpose[x][i]) in [Rook, Queen]:
                    return True

                break
        
        # no check has been registered

        return False
        
    @classmethod
    def get_moves(cls, piece, square, board, en_passant=[[], []]): # main cls method for finding moves
        # returns move according to piece input
        
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
        en_passant_moves = []

        # move forwards by 1
        if not board[y + piece.direction][x]:
            moves.append([x, y + piece.direction])
        
        # move forwards by 2 if piece is not moved
        if not piece.moved and not board[y + (2*piece.direction)][x]:
            moves.append([x, y + (2*piece.direction)])

        # take piece left
        if x > 0 and board[y + piece.direction][x-1] and not board[y + piece.direction][x-1].colour == colour:
            moves.append([x-1, y + piece.direction])

        # take piece right
        if x < 7 and board[y + piece.direction][x+1] and not board[y + piece.direction][x+1].colour == colour:
            moves.append([x+1, y + piece.direction])

        # check if there are available pawns to perform en passant
        if x < 7:
            right = board[y][x+1]

            if right and type(right) == Pawn and not right.colour == colour and [x+1, y] in en_passant[right.colour]:
                if (y == 4 and colour) or (y == 3 and not colour):
                    en_passant_moves.append([x+1, y + piece.direction])

        if x > 0:
            left = board[y][x-1]

            if left and type(left) == Pawn and not left.colour == colour and [x-1, y] in en_passant[left.colour]:
                if (y == 4 and colour) or (y == 3 and not colour):
                    
                    en_passant_moves.append([x-1, y + piece.direction])

        return moves, en_passant_moves

    @classmethod
    def get_king_moves(cls, square, board):
        x, y = square
        piece = board[y][x]
        colour = piece.colour
        moves = []
        castle_moves = []

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

            # left side castle
            can_castle_left = True

            # checks if squares are empty and not under check
            for x_left in reversed(range(x-2, x)):
                if board[y][x_left] or cls.in_check(colour, board, [x_left, y]):
                    can_castle_left = False
                    break

            # if above is met, checks if end rook is present and unmoved
            if can_castle_left:
                p_left = board[y][0]
                
                if p_left and type(p_left) == Rook and p_left.colour == colour:
                    castle_moves.append([x_left, y])

            # right side castle
            can_castle_right = True

            # checks if squares are empty and not under check
            for x_right in range(x+1, x+3):
                if board[y][x_right] or cls.in_check(colour, board, [x_right, y]):
                    can_castle_right = False
                    break

            # if above is met, checks if end rook is present and unmoved
            if can_castle_right:
                p_right = board[y][-1]

                if p_right and type(p_right) == Rook and p_right.colour == colour:
                    castle_moves.append([x_right, y])
                
        return moves, castle_moves

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
