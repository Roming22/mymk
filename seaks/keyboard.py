from time import sleep
import keypad


class Keyboard:
    def __init__(self, rows: list, cols: list) -> None:
        self._km = keypad.KeyMatrix(
            row_pins=rows,
            column_pins=cols,
        )

    def get_events(self):
        while True:
            # print(end=".")

            if event := self._km.events.get():
                print(
                    event.timestamp,
                    "Key",
                    event.key_number,
                    f"has been {'pressed' if event.pressed else 'released'}",
                )
                sleep(0.01)
