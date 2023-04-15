from collections import OrderedDict

import board

from seaks.logic.keyboard import Keyboard


def main() -> None:
    print("\n" * 8)
    print("#" * 120)

    definition = {
        "hardware": {
            "pins": {
                "cols": (
                    board.D26,
                    board.D22,
                    board.D20,
                    board.D23,
                ),
                "rows": (board.D6, board.D7, board.D9),
            },
            "leds": {
                "pin": None,
                "count": 0,
            },
            "split": True,
        },
        "layout": {"layers": OrderedDict()},
    }
    definition["layout"]["layers"]["alpha"] = {
        "keys": [
            # fmt: off
    "ESC",  "D",    "C",        "L",
    "NO",   "T",    "A",        "E",
            "NO",   "SPACE",    "LGUI", "LY_TO(symbols)",

            "R",    "S",    "H",    "ENTER",
            "I",    "O",    "N",    "NO",
    "NO",   "RGUI", "MEH",  "NO",
            # fmt: on
        ]
    }
    definition["layout"]["layers"]["symbols"] = {
        "keys": [
            # fmt: off
    None,   "GRAVE",    "BACKSLASH",    "UNDERSCORE",
    None,   "HASH",     "DOLLAR",       "EXCLAIM",
            None,       None,           None,           "LY_TO(alpha)",

            "MINUS",    "SLASH",    "EQUAL",    None,
            "DOT",      "COMMA",    "QUOTE",    None,
    None,   None,       None,       None,
            # fmt: on
        ],
    }
    keyboard = Keyboard(definition)

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
    # for switch, keycode in enumerate(["A", "B", "C"]):
    #     Key(
    #         "board.alpha",
    #         keyboard.board.hardware_board.get_switch_id(switch + 1),
    #         keycode,
    #     )

    # # Alpha2
    # for switch, key_name in enumerate(["D", "E", "F"]):
    #     Key(("board.alpha2", hardware_board.get_switch_id(switch + 1)), key_name)

    # # C,A = G
    # Sequence([("board.alpha", "03"), ("board.alpha", "01")], "G", 1.0)
    # # Sequence(["F", "E", "D"], "H")
    # # Chord(["B", "C"], "I")
    # # Chord(["A", "B", "C"], "J")

    # # Just for fun, let's allow the user to chain HOLD action together
    # TapHold(("board.alpha1", "01"), ["A", "K", "L"], 0.5)

    keyboard.go()


if __name__ == "__main__":
    main()
