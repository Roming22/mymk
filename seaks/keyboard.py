from time import sleep
import keypad

from seaks.event import Event


class Keyboard:
    def __init__(self, rows: list, cols: list) -> None:
        self._km = keypad.KeyMatrix(
            row_pins=rows,
            column_pins=cols,
        )

    def get_events(self):
        while True:
            if base_event := self._km.events.get():
                event = Event(
                    base_event.timestamp,
                    f"key{base_event.key_number}",
                    base_event.pressed,
                )
                print(event)
