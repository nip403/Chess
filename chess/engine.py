from chess.core import Engine
import pygame
import math
import sys
import os

#TODO download chess font file for text engine

"""

INPUT COMMANDS (non case sensitive)

exit            - Exits 

pgn             - Outputs PGN
localpgn        - Outputs formatted raw move list
*explicitpgn    - Outputs PGN with comprehensive algebraic notation

*pgncopy        - Outputs PGN (in the input format for importpgn)
getlocalpgn     - Outputs raw move list (in the input format for importlocalpgn)

*importpgn      - Input PGN for existing game
importlocalpgn  - Input raw move list for existing game

*fen            - Output copmlete FEN
*fenboard       - Outputs only FEN info which describes board

*inputfen       - Input copmlete FEN for existing game


add draw, resign, accept (draw/resign) commands
"""

"""
                Base
"""
class _chess:
    def __init__(self, engineid=0):
        self._build_engine(engineid)
        self.engine_id = engineid
        self.pgn = [] # N.B. pgn is written in full, with pieces upper/lower case with colour
        self._pgn = [] # pgn in input format (e.g. [["e2e4", "e7e5"], ["g1f3", "b8c6"]])

    def _build_engine(self, _id):
        if not _id:
            self.engine = Engine()
        else:
            raise Exception("Engine ID not found.")

    def print_instructions(self):
        print("""\
Moves should be input in the form:
    [Start Square][End Square]
e.g.
    g1f3

Illegal/invalid move inputs will be flagged.
The board will be printed out after every turn.\n""")

    def display_board(self):
        print()

        for p, row in enumerate(self.engine.board if not self.engine.turn else self.engine.board[::-1]):
            print(8-p if self.engine.turn else p+1, end=" ") # changes row number according to turn

            for piece in (row if self.engine.turn else row[::-1]): # rotation of board
                if not piece:
                    print(" ", end=" ")
                else:
                    if not piece.colour:
                        print(piece.__class__.__name__[0].lower() if not piece.__class__.__name__ == "Knight" else "n", end=" ")
                    else:
                        print(piece.__class__.__name__[0] if not piece.__class__.__name__ == "Knight" else "N", end=" ")

            print() 

        print(" " + ("ABCDEFGH".replace("", " ") if self.engine.turn else "HGFEDCBA".replace("", " "))) # changes column according to turn

    def reset(self, _id=None):
        self.__init__(self, self.engine_id if not _id is None else _id)

"""
                Graphics Engine
"""
class Chess(_chess):
    def __init__(self, dimensions=[800, 800], engineid=0):
        super().__init__(engineid)
        self._init_graphics(dimensions)

    def move(self, *move):
        notation, coords = move
        print(notation, coords)

        #while True:
         #   self.move_event_listener()


    def move_event_listener(self):
        pass

    def play(self):
        self.draw()

        while True:
            if self.main_event_listener():
                self.draw()

    def draw(self):
        for x in range(8):
            for y in range(8):
                pygame.draw.rect(self.surf, [238, 220, 180] if ((not x % 2 and not y % 2) or (x % 2 and y % 2)) else [180, 135, 100], [x * self.l, y * self.l, self.l, self.l], 0)
                
                piece = self.engine.board[7-y if self.engine.turn else y][x if self.engine.turn else 7-x]
                
                if not piece:
                    continue

                icon = self.img[piece.colour][piece.__class__.__name__.capitalize()]
                self.surf.blit(icon, icon.get_rect(center=[x * self.l + (self.l/2), y * self.l + (self.l/2)]))

        for p, i in enumerate(self.letters if self.engine.turn else self.letters[::-1]):
            self.surf.blit(i, i.get_rect(center=[p * self.l + (9*self.l/10), self.s[1] - self.l/8]))

        for p, i in enumerate(self.numbers if not self.engine.turn else self.numbers[::-1]):
            self.surf.blit(i, i.get_rect(center=[self.l/8, p * self.l + (self.l/10)]))

        pygame.display.flip()

    def main_event_listener(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.move(*self._parse_coords(pygame.mouse.get_pos()))
                return True

    #move event listener

    def _parse_coords(self, mouse):
        mouse = list(map(lambda i: int(i/self.l), mouse))
        key = sorted("A B C D E F G H".split(), reverse=not self.engine.turn)
        print([i[self.engine.turn] for i in [[7 - mouse[0], mouse[0]], [7 - mouse[1], mouse[1]]]])

        return key[mouse[0]] + str(8 - mouse[1] if self.engine.turn else mouse[1] + 1), [i[self.engine.turn] for i in [[7 - mouse[0], mouse[0]], [mouse[1], 7 - mouse[1]]]]

    def _init_graphics(self, d):
        pygame.init()
        assert len(d) == 2 and d[0] == d[1], "Invalid screen resolution."

        self.s = d
        self.l = math.ceil(d[0]/8)

        self.surf = pygame.display.set_mode(self.s, 0, 32)
        pygame.display.set_caption(self.engine.meta)
        
        self._init_icons()
        self._init_text()

    def _init_icons(self):
        self.img = [ # load piece images
            { # black (index 0), white (index 1)
                name.capitalize(): pygame.image.load(os.path.dirname(os.path.realpath(__file__)) + f"\\img\\{colour}_{name}.png").convert_alpha() for name in "pawn, rook, knight, bishop, queen, king".split(", ")
            } for colour in ["black", "white"]
        ]

        # resize
        for i in self.img:
            for name, img in i.items():
                i[name] = pygame.transform.smoothscale(img, [int(self.l * 0.9)]*2)

    def _init_text(self):
        """
        it was found that the size to pixel conversion for the windows font has
        an equation of pixels = 4/3 font size

        data was taken from "https://websemantics.uk/tools/font-size-conversion-pixel-point-em-rem-percent/"
        """
        
        self.font = pygame.font.SysFont("arial", round(0.75 * (self.l/5)), bold=True)
        self.letters = [self.font.render(letter, True, (0, 0, 0)) for letter in "A B C D E F G H".split()]
        self.numbers = [self.font.render(num, True, (0, 0, 0)) for num in "1 2 3 4 5 6 7 8".split()]

"""
                Text Engine
"""
class ChessText(_chess): 
    def __init__(self, engineid=0):
        super().__init__(engineid)
        self.print_instructions()
        self.display_board()

    def input(self):
        if self.engine.checkmate():
            return "1-0 Checkmate" if not self.engine.turn else "0-1 Checkmate" # checkmate only registers on opponent's turn

        elif self.engine.stalemate():
            return "1/2-1/2 Stalemate"

        # input move, validate and parse
        move = input(f"\n{['Black', 'White'][self.engine.turn]}'s move: ").upper()
        legal, parsed = self._parse_input(move)

        # custom commands
        if " " in move:
            move, *data = move.strip().split()

        if move == "EXIT":
            sys.exit()

        elif move == "GETLOCALPGN":
            print("\nLocalPGN:", " ".join(" ".join(i) for i in self._pgn))
            return

        elif move == "LOCALPGN":
            print("\nLocalPGN:")

            for p, move in enumerate(self._pgn):
                print(f"{p+1}.", " ".join(move))

            return

        #elif move == "PGN":
        #    print("\nPGN:")

        #    for p, move in enumerate(self.pgn):
        #        print(f"{p+1}.", " ".join(move))

        #    return 

        elif move == "IMPORTLOCALPGN":
            if not "data" in locals():
                return "LocalPGN not attatched."

            data = list(map(lambda i: i.upper(), data))

            if not self._validate_local_pgn(data): # update to walrus := 
                return "Invalid input localPGN."

            self.engine.build_from_localpgn(data)
            self.display_board()

            return

        if not legal:
            return "Invalid move, re-enter."

        # create copy for pgn conversion
        tmp_board = self.engine.board[:]

        # send move to engine, validate and process
        resp, additional = self.engine.move(parsed, self)

        if not resp:
            return additional

        # pgn
        if not self._pgn or len(self._pgn[-1]) == 2:
            if not "O" in additional:
                self._pgn.append([move.lower() + additional])
            else:
                self._pgn.append([additional])
        else:
            if not "O" in additional:
                self._pgn[-1].append(move.lower() + additional)
            else:
                self._pgn[-1].append(additional)

        """fix convert pgn method
        converted = self._convert_pgn(parsed, tmp_board)
        if not self.pgn or len(self.pgn[-1]) == 2:
            self.pgn.append([converted])
        else:
            self.pgn[-1].append(converted)
        """
            
        # print board
        self.display_board()

    def _validate_local_pgn(self, pgns):
        for i in pgns:
            if "-" in i and (not len(i.split("-") in [2, 3]) or not "O" in i):
                return False

            else:
                if not (i[1]+i[3]).isdecimal() or not 0 <= int(i[1]) < 8 or not 0 <= int(i[3]) < 8 or not all(65 <= ord(j) <= 72 for j in i[::2]):
                    return False

                if not len(i) in [4, 6, 8]:
                    return False

                if len(i) == 6 and (not i[-2] == "=" or not i[-1] in "QBRK"):
                        return False

                elif len(i) == 8 and not i[4:] == "e.p.":
                    return False

        return True

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

    #@property
    #def FEN

    def _convert_pgn(self, move, tmp):
        start, end = move

        sx = "ABCDEFGH".index(start[0])
        sy = int(start[1]) - 1

        ex = "ABCDEFGH".index(end[0])
        ey = int(end[1]) - 1

        start = start.lower()
        end = end.lower()

        piece = self.engine.board[ey][ex]
        n = piece.__class__.__name__

        if n == "Pawn":
            if tmp[ey][ex] and not tmp[ey][ex].colour == piece.colour:
                return start[0] + "x" + end
            else:
                return end
        
        return n[0] + ("x" if tmp[ey][ex] and not tmp[ey][ex].colour == piece.colour else "") + end
