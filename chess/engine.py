from chess.core import Engine
import pygame
import sys

"""
                Base
"""
class _chess:
    def __init__(self, engineid=0):
        self._build_engine(engineid)
        self.pgn = [] # N.B. pgn is written in full, with pieces upper/lower case with colour

    def _build_engine(self, _id):
        if not _id:
            self.engine = Engine()
        else:
            raise Exception("Engine ID not found.")

    def reset(self, _id=0):
        self.__init__(self, _id)

"""
                Graphics Engine
"""
class Chess(_chess):
    def __init__(self, dimensions=[800, 800], engineid=0):
        super().__init__(engineid)
        self._init_graphics(dimensions)
    
    def _build_engine(self, id):


        self.surf = pygame.display.set_mode(self.s, 0, 32)
        self.display.set_caption(self.chess.meta)

    def play(self):
        while True:
            pass

    def input(self):
        pass

"""
                Text Engine
"""
class ChessText(_chess): 
    def __init__(self, engineid=0):
        super().__init__(engineid)

    def input(self):
        # input move, validate and parse
        move = input(f"{['Black', 'White'][self.engine.turn]}'s move: ").upper()
        legal, parsed = self._parse_input(move)

        if move == "EXIT":
            sys.exit()

        if not legal:
            return "Invalid move, re-enter."

        # send move to engine, validate and process
        resp = self.engine.move(parsed, self)

        if resp == "X":
            return "Checkmate"
        elif resp == "x":
            return "Stalemate"
        elif not resp:
            return "Illegal move, re-enter."

        # pgn
            
        # print board
        self.engine.display_board()

    #@property
    #def FEN

    def _promotion_choice(self):
        while True:
            choice = input("Promote pawn to Q/R/B/K: ").upper()

            if len(choice) == 1 and choice in "QRBK":
                return choice

    def _parse_input(self, move): # validation
        if not len(move) == 4 or move[:2] == move[-2:]:
            return False, None

        letters = [move[0], move[2]]
        nums = [move[1], move[3]]

        if not all(64 < ord(m) < 73 for m in letters):
            return False, None

        if not all(n.isdigit() and 0 < int(n) < 9 for n in nums):
            return False, None

        return True, [move[:2], move[2:]]

