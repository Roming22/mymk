import seaks.utils.memory as memory
from seaks.features import Chord, Key, Sequence, TapHold
from seaks.hardware.board import Board as PhysicalBoard
from seaks.logic.action import Action
from seaks.logic.controller import Controller
from seaks.logic.event import Event
from seaks.logic.fps import FPS
from seaks.utils.memory import memory_cost
from seaks.virtual.board import Board


class Keyboard:
    @memory_cost("Keyboard")
    def __init__(self, row_pins: list, col_pins: list) -> None:
        mem_used = memory.get_usage()
        physical_board = PhysicalBoard(row_pins, col_pins)
        board = Board(physical_board, "board", ["alpha1", "alpha2"])
        self.board = board

        # Layer0/Layer1 transitions
        board.machine["alpha1"].add_trigger(
            Event.get("board.alpha1.switch.4", True),
            Action.chain(
                Action.state(board.machine, "alpha2"),
                Action.trigger("board.alpha1", False),
                Action.trigger("board.alpha2", True),
            ),
        )
        board.machine["alpha2"].add_trigger(
            Event.get("board.alpha2.switch.4", False),
            Action.chain(
                Action.state(board.machine, "alpha2"),
                Event.get("board.alpha1", False),
                Event.get("board.alpha2", True),
            ),
        )

        # Alpha1
        for switch, key_name in enumerate(["A", "B", "C"]):
            Key(("board.alpha1", physical_board.get_switch_id(switch + 1)), key_name)

        # Alpha2
        for switch, key_name in enumerate(["D", "E", "F"]):
            Key(("board.alpha2", physical_board.get_switch_id(switch + 1)), key_name)

        # Sequence(["C", "A"], "G")
        # Sequence(["F", "E", "D"], "H")
        # Chord(["B", "C"], "I")
        # Chord(["A", "B", "C"], "J")

        # Just for fun, let's allow the user to chain HOLD action together
        # TapHold(("0", 1), ["A", "K", "L"], 0.5)

        print("\n\nMemory used: ", memory.get_usage() - mem_used, "\n\n")

    def go(self, fps=False):
        fps = True
        print("\n\n\n")
        self.board.start()
        if fps:
            FPS.start(60)
        while True:
            if fps:
                FPS.tick()
            Controller.run()
