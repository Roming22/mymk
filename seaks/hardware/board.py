import keypad

from seaks.controller import Controller, Ticker
from seaks.event import Trigger


class Board(Ticker):
    def __init__(self, rows: list, cols: list) -> None:
        self._keymatrix = keypad.KeyMatrix(
            row_pins=rows,
            column_pins=cols,
        )
        Controller.set_board(self)

    def tick(self):
        if event := self._keymatrix.events.get():
            Trigger(f"switch.{event.key_number}", event.pressed).fire()
            Trigger(f"switch.any", event.pressed).fire()
