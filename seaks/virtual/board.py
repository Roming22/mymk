from collections import namedtuple

from seaks.hardware.board import Board as PhysicalBoard
from seaks.logic.controller import Controller, Ticker
from seaks.logic.event import Event
from seaks.logic.state import StateMachine
from seaks.utils.memory import memory_cost
from seaks.virtual.layer import Layer

LightBoard = namedtuple("LightBoard", "name phy_board machine layers default_layers")


class Board(Ticker):
    instances: dict[str, "Board"] = {}

    @memory_cost("vBoard")
    def __init__(
        self, physical_board: PhysicalBoard, name: str, layer_names: list[str]
    ) -> None:
        Board.instances[name] = self
        self.physical_board = physical_board
        machine = StateMachine("board", layer_names)
        self.name = name
        self.machine = machine
        layers: dict[str, Layer] = {}
        self.layers = layers
        for layer_name in layer_names:
            layers[layer_name] = Layer(
                physical_board, f"{name}.{layer_name}", machine[layer_name]
            )
        Controller.set_board(self)
        self.default_layer = layer_names[0]

    def start(self):
        Event.get(f"{self.name}.{self.default_layer}", True).fire()
        self.machine.start()

    def tick(self, _: Event = None) -> None:
        if event := self.physical_board._keymatrix.events.get():
            switch_id = self.physical_board.get_switch_id(event.key_number)
            Event.get(f"switch.{switch_id}", event.pressed).fire()
