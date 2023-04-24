from collections import namedtuple

import seaks.logic.event_handler as EventHandler
from seaks.features.layer import ActiveLayer, Layer
from seaks.hardware.board import Board as HardwareBoard
from seaks.utils.memory import check_memory

Board = namedtuple(
    "Board",
    ["name", "hardware_board", "start", "tick"],
)

instances: dict[str, Board] = {}


@check_memory("virtual.Board")
def create(hardware_board: HardwareBoard, name: str, default_layer_name: str) -> Board:
    def start():
        Layer.activate_layer(default_layer_name)

    def get_event_id(event) -> str:
        switch_id = hardware_board.get_switch_id(event.key_number)
        if event.pressed:
            prefix = f"{name}.{ActiveLayer.get_layer_for(int(switch_id))}."
        else:
            prefix = "!"
        return f"{prefix}switch.{switch_id}"

    def tick() -> None:
        if event := hardware_board._keymatrix.events.get():
            event_id = get_event_id(event)
            print(f"\n# {event_id} {'#' * 120}"[:120])
            if event.pressed and EventHandler.has_interrupted(event_id):
                event_id = get_event_id(event)
            EventHandler.handle_event(event_id)

    board = Board(name, hardware_board, start, tick)
    instances[name] = board
    return board


def tick() -> None:
    for board in instances.values():
        board.tick()
