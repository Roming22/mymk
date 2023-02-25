import board

from time import sleep
from seaks.keyboard import Keyboard


def main() -> None:
    print("\n"*8)
    print("#"*120)
    keyboard = Keyboard(
        rows=(board.D5, board.D6, board.D7, board.D9),
        cols=(
            board.D27,
            board.D26,
            board.D22,
            board.D20,
            board.D23,
            board.D21,
        ),
    )
    keyboard.go()


if __name__ == "__main__":
    main()
