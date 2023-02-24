from seaks.action import Action
from seaks.controller import Controller
from seaks.event import Trigger
from seaks.features import Chord, Key, Layer, Sequence
from seaks.hardware.board import Board


class Keyboard:
    def __init__(self, rows: list, cols: list) -> None:
        Board(rows, cols)

        layers = Layer(["0", "1"])

        # Layer0
        for switch, key_name in enumerate(["A", "B", "C"]):
            Key(switch + 1, key_name, layers["0"])

        # Layer1
        for switch, key_name in enumerate(["D", "E", "F"]):
            Key(switch + 1, key_name, layers["1"])

        # Layer0/Layer1 transitions
        layers["0"].add_trigger(
            Trigger("switch.4", True),
            Action.state(layers, "1"),
        )
        layers["1"].add_trigger(
            Trigger("switch.4", False),
            Action.state(layers, "0"),
        )

        Chord(["B", "C"], "G")
        Sequence(["C", "A"], "H")
        Sequence(["F", "E", "D"], "I")

    def go(self):
        while True:
            Controller.run()
