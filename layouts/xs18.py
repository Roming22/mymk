from collections import OrderedDict

import board

from mymk.feature.keyboard import Keyboard


def main() -> None:
    print("\n" * 5)
    print("#" * 120)
    print("# BOOTING")
    print("#" * 120)

    # Hardware definition
    definition = {
        "hardware": {
            "xs18": {
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
                    "pin": board.D0,
                    "count": 4,
                    "RGB": (127, 63, 0),
                },
                "split": True,
            },
        },
        "layout": {"layers": OrderedDict()},
    }

    # Layer definitions

    ##  Alpha layer
    definition["layout"]["layers"]["alpha"] = {
        "keys": [
            # fmt: off
    "TH_HD(ESC,LSFT)",  "TH_HD(D, LSFT)",   "TH_HD(C,LALT)",    "TH_HD(L,LCTL)",
    "NO",               "T",                "A",                "E",
                        "NO",               "SPACE",            "LGUI",         "NO",

            "TH_HD(R,RCTL)",    "TH_HD(S,RALT)",    "TH_HD(H,RSFT)",    "TH_HD(ENTER,RSFT)",
            "I",                "O",                "N",                "NO",
    "NO",   "RGUI",             "MEH",              "NO",
            # fmt: on
        ],
        "combos": {
            "chords": {
                "1*2": "X",
                "2*3": "V",
                "1*3": "Z",
                "1*2*3": "ESCAPE",
                "5*6": "F",
                "6*7": "U",
                "5*7": "B",
                "5*6*7": "M",
                "12*13": "K",
                "13*14": "Q",
                "12*14": "J",
                "12*13*14": "BACKSPACE",
                "16*17": "Y",
                "17*18": "G",
                "16*18": "P",
                "18*17*16": "W",
            },
        },
    }

    ## Symbol layer
    # definition["layout"]["layers"]["symbols"] = {
    #     "keys": [
    #         # fmt: off
    # None,   "GRAVE",        "BACKSLASH",    "UNDERSCORE",
    # None,   "HASH",         "DOLLAR",       "EXCLAIM",
    #         "LY_TO(alpha)", None,           None,           None,

    #         "MINUS",    "SLASH",    "EQUAL",    None,
    #         "DOT",      "COMMA",    "QUOTE",    None,
    # None,   None,       None,       None,
    #         # fmt: on
    #     ],
    # }

    keyboard = Keyboard(definition)
    keyboard.go(True)


if __name__ == "__main__":
    main()
