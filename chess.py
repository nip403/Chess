from engine import Chess

def main():
    game = Chess()
    while True:
        msg = game.input()

        if msg is not None:
            print(msg)


if __name__ == "__main__":
    main()