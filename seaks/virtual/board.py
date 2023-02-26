from collections import namedtuple

from seaks.hardware.board import Board as HardwareBoard
from seaks.logic.controller import Controller, Ticker
from seaks.logic.event import Event
from seaks.logic.state import StateMachine
from seaks.utils.memory import memory_cost
from seaks.virtual.layer import create as create_layer

Board = namedtuple(
    "Board",
    ["name", "hardware_board", "machine", "layers", "default_layer", "start", "tick"],
)

instances: dict[str, Board] = {}


@memory_cost("vBoard")
def create(hardware_board: HardwareBoard, name: str, layer_names: list[str]) -> Board:
    if name in instances.keys():
        raise KeyError(f"A layer with the name '{name}' already exists.")
    machine = StateMachine("board", layer_names)
    layers: dict[str, Layer] = {}
    for layer_name in layer_names:
        layers[layer_name] = create_layer(
            hardware_board, f"{name}.{layer_name}", machine[layer_name]
        )
    default_layer = layer_names[0]

    def start():
        Event.get(f"{name}.{default_layer}", True).fire()
        machine.start()

    def tick(_: Event = None) -> None:
        if event := hardware_board._keymatrix.events.get():
            switch_id = hardware_board.get_switch_id(event.key_number)
            Event.get(f"switch.{switch_id}", event.pressed).fire()

    board = Board(name, hardware_board, machine, layers, default_layer, start, tick)
    Controller.set_board(board)
    instances[name] = board
    return board
