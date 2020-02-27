from chess.engine import ChessText

def main():
    game = ChessText()

    while True:
        msg = game.input()

        if msg is not None:
            print(msg)

            if msg in ["Checkmate", "Stalemate"]:
                break

if __name__ == "__main__":
    main()
