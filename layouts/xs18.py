from time import sleep

import board

import seaks.utils.memory as memory
from seaks.features import Key
from seaks.logic.keyboard import Keyboard


def main() -> None:
    print("\n" * 8)
    print("#" * 120)
    mem_used = memory.get_usage()
    keyboard = Keyboard(
        row_pins=(board.D6, board.D7, board.D9),
        col_pins=(
            board.D26,
            board.D22,
            board.D20,
            board.D23,
        ),
        layers=["alpha", "symbols"],
    )
    print("\n\nMemory used for keyboard: ", memory.get_usage() - mem_used, "\n\n")

    # # Layer0/Layer1 transitions
    # board.machine["alpha1"].add_trigger(
    #     Event.get("board.alpha1.switch.04", True),
    #     Action.chain(
    #         Action.state(board.machine, "alpha2"),
    #         Action.trigger("board.alpha1", False),
    #         Action.trigger("board.alpha2", True),
    #     ),
    # )
    # board.machine["alpha2"].add_trigger(
    #     Event.get("board.alpha2.switch.04", False),
    #     Action.chain(
    #         Action.state(board.machine, "alpha1"),
    #         Action.trigger("board.alpha2", False),
    #         Action.trigger("board.alpha1", True),
    #     ),
    # )

    # # Alpha1
    for switch, keycode in enumerate(["A", "B", "C"]):
        Key(
            "board.alpha",
            keyboard.board.hardware_board.get_switch_id(switch + 1),
            keycode,
        )

    # # Alpha2
    # for switch, key_name in enumerate(["D", "E", "F"]):
    #     Key(("board.alpha2", hardware_board.get_switch_id(switch + 1)), key_name)

    # # C,A = G
    # Sequence([("board.alpha1", "03"), ("board.alpha1", "01")], "G", 0.3)
    # # Sequence(["F", "E", "D"], "H")
    # # Chord(["B", "C"], "I")
    # # Chord(["A", "B", "C"], "J")

    # # Just for fun, let's allow the user to chain HOLD action together
    # TapHold(("board.alpha1", "01"), ["A", "K", "L"], 0.5)

    keyboard.go()


if __name__ == "__main__":
    main()
