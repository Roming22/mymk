from collections import OrderedDict

import board

from seaks.logic.keyboard import Keyboard


def main() -> None:
    print("\n" * 8)
    print("#" * 120)

    # Hardware definition
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

    # Layer definitions

    ##  Alpha layer
    definition["layout"]["layers"]["alpha"] = {
        "keys": [
            # fmt: off
    "ESC",              "TH_HD(D, LSFT)",           "TH_HD(C, LALT)",   "TH_HD(L, LCTL)",
    "LY_MO(symbols)",   "TH_HD(T, LY_MO(symbols))", "A",                "E",
                        "LY_TO(symbols)",           "SPACE",            "LGUI",             "NO",

            "TH_HD(R, RSFT)",   "TH_HD(S, RALT)",   "TH_HD(H, RSFT)",   "ENTER",
            "I",                "O",                "N",                "NO",
    "NO",   "RGUI",             "MEH",              "NO",
            # fmt: on
        ]
    }

    ## Symbol layer
    definition["layout"]["layers"]["symbols"] = {
        "keys": [
            # fmt: off
    None,   "GRAVE",        "BACKSLASH",    "UNDERSCORE",
    None,   "HASH",         "DOLLAR",       "EXCLAIM",
            "LY_TO(alpha)", None,           None,           None,

            "MINUS",    "SLASH",    "EQUAL",    None,
            "DOT",      "COMMA",    "QUOTE",    None,
    None,   None,       None,       None,
            # fmt: on
        ],
    }

    # Combo definitions
    definition["layout"]["combos"] = {
        ## Chords (can be pressed in any order)
        "chords": {
            # "board.layer.alpha.switch.1+board.layer.alpha.switch.2+board.layer.alpha.switch.3": "DELETE",
            "board.layer.alpha.switch.6+board.layer.alpha.switch.7": "Y",
        },
        ## Sequences (must be pressed in the order defined)
        "sequences": {
            "board.layer.alpha.switch.5+board.layer.alpha.switch.6": "W",
        },
    }

    keyboard = Keyboard(definition)
    keyboard.go()


if __name__ == "__main__":
    main()
