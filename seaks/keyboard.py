from time import sleep
import keypad

from seaks.action import Action
from seaks.event import Event
from seaks.event import Trigger
from seaks.state import StateMachine, State


class Keyboard:
    def __init__(self, rows: list, cols: list) -> None:
        self._km = keypad.KeyMatrix(
            row_pins=rows,
            column_pins=cols,
        )
        sm = StateMachine("keyboard")
        sm.new_state("default")
        sm.new_state("key2")

        sm.states["default"].add_trigger(Trigger("key2", True), Action(lambda: Keyboard.do_something),sm.states["key2"])
        sm.states["key2"].add_trigger(Trigger("key1", True), Action(lambda: Keyboard.do_something),sm.states["default"])

    @staticmethod
    def do_something():
        print("Do something")
        return True

    def get_events(self):
        while True:
            if base_event := self._km.events.get():
                event = Event.notify(
                    f"key{base_event.key_number}",
                    base_event.pressed,
                    base_event.timestamp,
                )
