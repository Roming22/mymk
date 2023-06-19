import mymk.feature
from mymk.feature.layers.layer_manager import LayerManager
from mymk.hardware.board import Board
from mymk.logic.timer import Timer
from mymk.multiverse.timeline_manager import TimelineManager
from mymk.utils.fps import FPS
from mymk.utils.memory import get_usage, memory_cost
from mymk.utils.time import Time
from mymk.utils.toolbox import debug_mode, debug


class Keyboard:
    @memory_cost("Keyboard")
    def __init__(self, definition: dict) -> None:
        board = Board(definition)
        self.board = board

        if board.is_controller:
            debug("Controller board")
            self.load_layers(board, definition)
        else:
            debug("Extension board")

        if len(definition["hardware"]) > 1 and not board.is_left:
            left_board_definition = [
                v for k, v in definition["hardware"].items() if k.endswith("L")
            ][0]
            switch_count_left = len(left_board_definition["pins"]["cols"]) * len(
                left_board_definition["pins"]["rows"]
            )
            board.switch_offset = switch_count_left
            debug("Board is on the right", switch_count_left)

    def load_layers(self, board: Board, definition: dict) -> None:
        switch_count = 0
        for b_d in definition["hardware"].values():
            switch_count += len(b_d["pins"]["cols"]) * len(b_d["pins"]["rows"])

        # Load layers
        for layer_name, layer_definition in definition["layout"]["layers"].items():
            LayerManager.load(board.name, layer_name, layer_definition, board.pixels)
            key_definitions = layer_definition["keys"]
            key_count = len(key_definitions)
            if key_count != switch_count:
                raise RuntimeError(
                    f"Invalid key count on layer '{layer_name}'. Layer has {key_count} keys, expected {switch_count}."
                )

        if debug_mode:
            debug(get_usage(True))

        default_layer = definition["settings"]["default_layer"]
        TimelineManager.activate(default_layer)
        LayerManager.get(default_layer).set_leds()

    def go(self):
        if debug_mode:
            FPS.start(60)

        while True:
            self.tick()
            if debug_mode:
                FPS.tick(check_memory=True)

    def tick(self):
        Time.tick()
        Timer.tick()
        self.board.tick()
