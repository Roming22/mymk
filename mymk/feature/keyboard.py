from mymk.feature.layers.layer_manager import LayerManager
from mymk.hardware.board import Board
from mymk.logic.timer import Timer
from mymk.multiverse.timeline_manager import TimelineManager
from mymk.utils.fps import FPS
from mymk.utils.memory import get_usage, memory_cost, profile


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
            default_layer = ""
            for layer_name, layer_definition in definition["layout"]["layers"].items():
                if not default_layer:
                    default_layer = layer_name
                LayerManager.load(board.name, layer_name, layer_definition)

                key_definitions = layer_definition["keys"]
                key_count = len(key_definitions)
                if key_count != switch_count:
                    raise RuntimeError(
                        f"Invalid key count on layer '{layer_name}'. Layer has {key_count} keys, expected {switch_count}."
                    )

            self.boards.append(board)
            TimelineManager.activate(default_layer)

        if not profile:
            print(get_usage(True))

    def go(self, fps=False):
        if fps:
            FPS.start(60)

        print("\n" * 3)
        print("#" * 120)
        print("# ONLINE")
        print("#" * 120)

        while True:
            if fps:
                FPS.tick(True)
            self.tick()

    def tick(self):
        Timer.tick()
        for board in self.boards:
            board.tick()
