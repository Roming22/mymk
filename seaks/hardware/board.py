import keypad

from seaks.hardware.switch import Switch
from seaks.utils.memory import memory_cost


class Board:
    @memory_cost("Board")
    def __init__(self, row_pins: list, col_pins: list) -> None:
        self._keymatrix = keypad.KeyMatrix(
            row_pins=row_pins,
            column_pins=col_pins,
        )
        self.switch_id_width = len(f"{len(row_pins) * len(col_pins)}")
        self.switches = Switch.instanciate_matrix(
            "board", len(row_pins), len(col_pins), self.get_switch_id
        )

    def get_switch_id(self, id: int) -> str:
        return "{id:0{width}d}".format(id=id, width=self.switch_id_width)
