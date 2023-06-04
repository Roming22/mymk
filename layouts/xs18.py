from collections import OrderedDict

import board

import mymk.feature.keys.taphold
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
                    "pin": None,
                    "count": 0,
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
            "1+2": "X",
            "2+1": "X",
            "2+3": "V",
            "3+2": "V",
            "1+3": "Z",
            "3+1": "Z",
            "5+6": "F",
            "6+5": "F",
            "6+7": "U",
            "7+6": "U",
            "5+7": "P",
            "7+5": "P",
            "5+6+7": "W",
            "12+13": "K",
            "13+12": "K",
            "13+14": "Q",
            "14+13": "Q",
            "12+14": "J",
            "14+12": "J",
            "16+17": "Y",
            "17+16": "Y",
            "17+18": "G",
            "18+17": "G",
            "16+18": "M",
            "18+16": "M",
            "18+17+16": "B",
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
