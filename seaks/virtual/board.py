from seaks.hardware.board import Board as PhysicalBoard
from seaks.logic.controller import Controller, Ticker
from seaks.logic.event import Event, Trigger
from seaks.logic.state import StateMachine
from seaks.virtual.layer import Layer


class Board(Ticker):
    instances: dict[str, "Board"] = {}

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
        Trigger(f"{self.name}.{self.default_layer}", True).fire()
        self.machine.start()

    def tick(self, _: Event = None) -> None:
        if event := self.physical_board._keymatrix.events.get():
            switch_id = self.physical_board.get_switch_id(event.key_number)
            Trigger(f"switch.{switch_id}", event.pressed).fire()
