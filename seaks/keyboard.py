from time import sleep
import keypad

from seaks.event import Event
from seaks.state import StateMachine, State


class Keyboard:
    def __init__(self, rows: list, cols: list) -> None:
        self._km = keypad.KeyMatrix(
            row_pins=rows,
            column_pins=cols,
        )
        sm = StateMachine("keyboard")
        sm.add_state(State("default"))

    def get_events(self):
        while True:
            if base_event := self._km.events.get():
                event = Event.notify(
                    f"key{base_event.key_number}",
                    base_event.pressed,
                    base_event.timestamp,
                )
