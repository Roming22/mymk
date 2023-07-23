import mymk.feature as _
import mymk.feature.layers.layer_manager as LayerManager
import mymk.utils.fps as FPS
from mymk.hardware.board import Board
from mymk.logic.timer import Timer
from mymk.multiverse.timeline_manager import TimelineManager
from mymk.utils.logger import logger
from mymk.utils.memory import get_usage, memory_cost, profile
from mymk.utils.time import Time


class Keyboard:
    @memory_cost("Keyboard")
    def __init__(self, definition: dict) -> None:
        board = Board(definition)
        self.board = board
        self.load_layers(board, definition)

    def load_layers(self, board: Board, definition: dict) -> None:
        switch_count = 0
        for b_d in definition["hardware"].values():
            switch_count += len(b_d["matrix"]["cols"]) * len(b_d["matrix"]["rows"])

        # Load layers
        for layer_name, layer_definition in definition["layout"]["layers"].items():
            LayerManager.load(board, layer_name, layer_definition)
            key_definitions = layer_definition["keys"]
            key_count = len(key_definitions)
            if key_count != switch_count:
                raise RuntimeError(
                    f"Invalid key count on layer '{layer_name}'. Layer has {key_count} keys, expected {switch_count}."
                )

        if not profile:
            logger.info(get_usage(True))

        default_layer = definition["settings"]["default_layer"]
        TimelineManager.activate(default_layer)
        LayerManager.get(default_layer).set_leds()

    def go(self, fps: bool = False) -> None:
        if fps:
            FPS.start(60)

        while True:
            self.tick()
            if fps:
                FPS.tick(True)

    def tick(self) -> None:
        Time.tick()
        Timer.tick()
        self.board.tick()
