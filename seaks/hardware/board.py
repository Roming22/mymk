from collections import namedtuple

import keypad

from seaks.hardware.switch import instanciate_matrix
from seaks.utils.memory import memory_cost

Board = namedtuple("Board", ["_keymatrix", "get_switch_id", "switches"])


def create(row_pins: list, col_pins: list) -> Board:
    keymatrix = keypad.KeyMatrix(
        row_pins=row_pins,
        column_pins=col_pins,
    )

    switch_id_width = len(f"{len(row_pins) * len(col_pins)}")

    def get_switch_id(id: int) -> str:
        return "{id:0{width}d}".format(id=id, width=switch_id_width)

    switches = instanciate_matrix("board", len(row_pins), len(col_pins), get_switch_id)
    board = Board(keymatrix, get_switch_id, switches)
    return board
