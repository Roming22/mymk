from seaks.features.layer import Layer
from seaks.hardware.board import create as create_hardware_board
from seaks.logic.controller import Controller
from seaks.logic.fps import FPS
from seaks.utils.memory import get_usage, memory_cost, profile
from seaks.virtual.board import create as create_board


class Keyboard:
    @memory_cost("Keyboard")
    def __init__(self, definition: dict, board_uid="board") -> None:
        hardware_board = create_hardware_board(
            definition["hardware"]["pins"]["rows"],
            definition["hardware"]["pins"]["cols"],
        )
        try:
            board = create_board(
                hardware_board,
                board_uid,
                list(definition["layout"]["layers"].keys())[0],
            )
        except IndexError:
            raise RuntimeError("'layout.layers' must have at least one layer defined.")

        switch_count = (
            len(definition["hardware"]["pins"]["cols"])
            * len(definition["hardware"]["pins"]["rows"])
            * 2 ** int(definition["hardware"]["split"])
        )
        for layer_name, layer_definition in definition["layout"]["layers"].items():
            Layer(board, layer_name, layer_definition)

            key_definitions = layer_definition["keys"]
            key_count = len(key_definitions)
            if key_count != switch_count:
                raise RuntimeError(
                    f"Invalid key count on layer '{layer_name}'. Layer has {key_count} keys, expected {switch_count}."
                )

        self.board = board

        if not profile:
            print(get_usage(True))

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
