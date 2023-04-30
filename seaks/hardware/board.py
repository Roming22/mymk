from collections import namedtuple

import keypad

from seaks.hardware.switch import instanciate_matrix
from seaks.utils.memory import check_memory

Board = namedtuple("Board", ["_keymatrix", "switches"])


@check_memory("hardware.Board")
def create(row_pins: list, col_pins: list) -> Board:
    keymatrix = keypad.KeyMatrix(
        row_pins=row_pins,
        column_pins=col_pins,
    )

    switches = instanciate_matrix("board", len(row_pins), len(col_pins))
    board = Board(keymatrix, switches)
    return board
