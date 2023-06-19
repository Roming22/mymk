import mymk.feature
from mymk.feature.layers.layer_manager import LayerManager
from mymk.hardware.board import Board
from mymk.logic.timer import Timer
from mymk.multiverse.timeline_manager import TimelineManager
from mymk.utils.fps import FPS
from mymk.utils.memory import get_usage, memory_cost, profile
from mymk.utils.time import Time


class Keyboard:
    @memory_cost("Keyboard")
    def __init__(self, definition: dict) -> None:
        self.boards = []
        for board_name, board_definition in definition["hardware"].items():
            board = Board(board_name, board_definition)

            # The switch count is doubled in case of a split keyboard
            switch_count = (
                len(board_definition["pins"]["cols"])
                * len(board_definition["pins"]["rows"])
                * 2 ** int(board_definition.get("split", False))
            )

            # Load layers
            for layer_name, layer_definition in definition["layout"]["layers"].items():
                LayerManager.load(
                    board.name, layer_name, layer_definition, board.pixels
                )
                key_definitions = layer_definition["keys"]
                key_count = len(key_definitions)
                if key_count != switch_count:
                    raise RuntimeError(
                        f"Invalid key count on layer '{layer_name}'. Layer has {key_count} keys, expected {switch_count}."
                    )

            self.boards.append(board)

        if not profile:
            print(get_usage(True))

        default_layer = definition["settings"]["default_layer"]
        TimelineManager.activate(default_layer)
        LayerManager.get(default_layer).set_leds()

    def go(self, fps=False):
        if fps:
            FPS.start(60)

        while True:
            self.tick()
            if fps:
                FPS.tick(True)

    def tick(self):
        Time.tick()
        Timer.tick()
        for board in self.boards:
            board.tick()
