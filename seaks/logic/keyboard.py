from collections import namedtuple

import seaks.utils.memory as memory
from seaks.hardware.board import create as create_hardware_board
from seaks.logic.action import Action
from seaks.logic.controller import Controller
from seaks.logic.event import Event
from seaks.logic.fps import FPS
from seaks.logic.state import StateMachine
from seaks.utils.memory import memory_cost
from seaks.virtual.board import create as create_board

# Aliases to improve code readability
chain = Action.chain
oneshot = Action.oneshot
press = Action.press
release = Action.release
set_state = Action.state


class Keyboard:
    @memory_cost("Keyboard")
    def __init__(self, definition: dict) -> None:
        mem_used = memory.get_usage()
        hardware_board = create_hardware_board(
            definition["hardware"]["pins"]["rows"],
            definition["hardware"]["pins"]["cols"],
        )
        board = create_board(hardware_board, "board", definition["layout"]["layers"])
        self.board = board
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
