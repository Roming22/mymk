from collections import namedtuple

from seaks.features.key import KeyTicker
from seaks.features.layer import ActiveLayer, Layer
from seaks.hardware.board import Board as HardwareBoard
from seaks.logic.buffer import Buffer
from seaks.logic.controller import Controller
from seaks.utils.memory import check_memory

Board = namedtuple(
    "Board",
    ["name", "hardware_board", "start", "tick"],
)

instances: dict[str, Board] = {}


@check_memory("virtual.Board")
def create(hardware_board: HardwareBoard, name: str, default_layer_name: str) -> Board:
    def start():
        KeyTicker()
        Layer.activate_layer(default_layer_name)

    def tick() -> None:
        if event := hardware_board._keymatrix.events.get():
            switch_id = hardware_board.get_switch_id(event.key_number)
            if event.pressed:
                prefix = f"{name}.{ActiveLayer.get_layer_for(int(switch_id))}."
            else:
                prefix = "!"
            Buffer.instance.register(f"{prefix}switch.{switch_id}")

    board = Board(name, hardware_board, start, tick)
    Controller.set_board(board)
    instances[name] = board
    return board
