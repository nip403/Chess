from chess.engine import ChessText
import os

def main():
    #game = GraphicsEngine(Chess(text=False), [800, 800])
    #game.play()

    #""" text based game:
    game = ChessText()

    while True:
        msg = game.input()

        if msg is not None:
            print(msg)

    #"""

if __name__ == "__main__":
    main()
