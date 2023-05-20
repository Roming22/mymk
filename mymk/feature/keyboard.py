from mymk.hardware.board import Board
# from seaks.features.layer import Layer
from seaks.logic.fps import FPS
# from seaks.logic.timer import Timer
from seaks.utils.memory import get_usage, memory_cost, profile


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
                * 2 ** int(board_definition["split"])
            )

            # Load layers
            # for layer_name, layer_definition in definition["layout"]["layers"].items():
            #     Layer(board, layer_name, layer_definition)

            #     key_definitions = layer_definition["keys"]
            #     key_count = len(key_definitions)
            #     if key_count != switch_count:
            #         raise RuntimeError(
            #             f"Invalid key count on layer '{layer_name}'. Layer has {key_count} keys, expected {switch_count}."
            #         )

            self.boards.append(board)

        if not profile:
            print(get_usage(True))

    def go(self, fps=False):
        fps = True
        print("\n\n\n")
        # self.board.start()
        if fps:
            FPS.start(60)
        while True:
            if fps:
                FPS.tick()
            # Timer.tick()
            for board in self.boards:
                board.tick()
