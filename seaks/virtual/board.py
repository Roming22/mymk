from collections import namedtuple

from seaks.features.key import KeyTicker
from seaks.hardware.board import Board as HardwareBoard
from seaks.logic.buffer import Buffer
from seaks.logic.controller import Controller
from seaks.logic.event import Event
from seaks.utils.memory import check_memory

Board = namedtuple(
    "Board",
    ["name", "hardware_board", "layers", "active_layers", "start", "tick"],
)

instances: dict[str, Board] = {}


@check_memory("vBoard")
def create(hardware_board: HardwareBoard, name: str, layer_names: list[str]) -> Board:
    if name in instances.keys():
        raise KeyError(f"A layer with the name '{name}' already exists.")
    active_layers = [layer_names[0]]

    def start():
        KeyTicker()
        Buffer.instance.register(f"{name}.{active_layers[0]}")

    def tick() -> None:
        if event := hardware_board._keymatrix.events.get():
            switch_id = hardware_board.get_switch_id(event.key_number)
            if event.pressed:
                prefix = f"{name}.{active_layers[0]}."
            else:
                prefix = "!"
            Buffer.instance.register(f"{prefix}switch.{switch_id}")

    board = Board(name, hardware_board, layer_names, active_layers, start, tick)
    Controller.set_board(board)
    instances[name] = board
    return board
