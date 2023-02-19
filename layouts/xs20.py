import board

from time import sleep
from seaks.keyboard import Keyboard


def main() -> None:
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
    for event in keyboard.get_events():
        print("Event: Key ", event[0], f"{'pressed' if event[1] else 'released'}")
        sleep(2)


if __name__ == "__main__":
    main()
