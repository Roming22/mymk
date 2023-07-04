import board
import supervisor

# try:
#     from mymk.feature.keyboard import Keyboard
# except OSError:
#     from mymk.hardware.extension import Keyboard

from mymk.utils.logger import logger


def get_definition():
    # Hardware definition
    definition = {
        "hardware": {
            "KEYBOARD-L": {
                "matrix": {
                    "cols": (
                        board.D26,
                        board.D22,
                        board.D20,
                        board.D23,
                    ),
                    "rows": (board.D6, board.D7, board.D9),
                },
                "data": {
                    "pin": board.D1,
                },
                "leds": {
                    "pin": board.D0,
                    "count": 4,
                },
            },
            "KEYBOARD-R": {
                "matrix": {
                    "cols": (
                        board.D23,
                        board.D20,
                        board.D22,
                        board.D26,
                    ),
                    "rows": (board.D6, board.D7, board.D9),
                },
                "data": {
                    "pin": board.D1,
                },
                "leds": {
                    "pin": board.D0,
                    "count": 4,
                },
            },
        },
        "layout": {
            "layers": {},
        },
        "settings": {
            "default_layer": "alpha",
        },
    }

    # Layer definitions

    ##  Alpha layer
    definition["layout"]["layers"]["alpha"] = {
        "leds": {
            "RGB": (127, 0, 0),
        },
        "keys": [
            # fmt: off
    "TH_HD(TAB,LSFT)",  "TH_HD(D, LSFT)",           "TH_HD(C,LALT)",            "TH_HD(L,LCTL)",
    "NO",               "TH_HD(T,LY_MO(systemL))",  "TH_HD(A,LY_MO(fn_numL))",  "TH_HD(E,LY_MO(symbolsL))",
                        "NO",                       "SPACE",                    "LGUI",                     "NO",

            "TH_HD(R,RCTL)",            "TH_HD(S,RALT)",            "TH_HD(H,RSFT)",            "TH_HD(ENTER,RSFT)",
            "TH_HD(I,LY_MO(symbolsR))", "TH_HD(O,LY_MO(fn_numR))",  "TH_HD(N,LY_MO(systemR)",   "NO",
    "NO",   "RGUI",                     "MEH",                      "NO",
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

    ## Symbol layers
    definition["layout"]["layers"]["symbols"] = {
        "leds": {
            "RGB": (127, 21, 0),
        },
        "keys": [
            # fmt: off
    None,   "GRAVE",        "BACKSLASH",    "UNDERSCORE",
    None,   "HASH",         "DOLLAR",       "EXCLAIM",
            "LY_TO(alpha)", None,           None,           None,

            "MINUS",    "SLASH",        "EQUAL",    None,
            "DOT",      "COMMA",        "QUOTE",    None,
    None,   None,       "LY_TO(alpha)", None,
            # fmt: on
        ],
        "chords": {
            "1*2": "<",
            "2*3": ">",
            "1*2*3": "ESCAPE",
            "5*6": "{",
            "6*7": "}",
            "12*13": "[",
            "13*14": "]",
            "12*13*14": "BACKSPACE",
            "16*17": "(",
            "17*18": ")",
        },
        "sequences": {
            "1+12": "",
            "1+13": "",
            "1+14": "",
            "1+16": "",
            "1+17": "",
            "1+18": "",
            "14+1": "",
            "14+2": "",
            "14+3": "",
            "14+5": "",
            "14+6": "",
            "14+7": "",
        },
    }
    definition["layout"]["layers"].update(
        generate_split(definition["layout"]["layers"], "alpha", "symbols")
    )

    ## Fn and nums layers
    definition["layout"]["layers"]["fn_num"] = {
        "leds": {
            "RGB": (127, 42, 0),
        },
        "keys": [
            # fmt: off
    None,   "F1",   "F3",   "F5",
    None,   "F7",   "F9",   "F11",
            "LY_TO(alpha)", None,           None,           None,

            "5",    "7",            "9",    None,
            "0",    "2",            "4",    None,
    None,   None,   "LY_TO(alpha)", None,
            # fmt: on
        ],
        "combos": {
            "chords": {
                "1*2": "F2",
                "2*3": "F4",
                "1*3": "F6",
                "1*2*3": "ESCAPE",
                "5*6": "F8",
                "6*7": "F10",
                "5*7": "F12",
                "12*13": "6",
                "13*14": "7",
                "12*13*14": "BACKSPACE",
                "16*17": "1",
                "17*18": "3",
            },
        },
    }
    definition["layout"]["layers"].update(
        generate_split(definition["layout"]["layers"], "alpha", "fn_num")
    )

    ## System layers
    definition["layout"]["layers"]["system"] = {
        "leds": {
            "RGB": (127, 0, 127),
        },
        "keys": [
            # fmt: off
    None,   "ESC",  "PAGEUP",   "PRTSCR",
    None,   "HOME", "PAGEDOWN", "END",
            None,   None,       None,       None,

            "BACKSPACE",    "UP",   "DELETE",   None,
            "LEFT",         "DOWN", "RIGHT",    None,
    None,   None,           "LY_TO(alpha)",     None,
            # fmt: on
        ],
    }
    definition["layout"]["layers"].update(
        generate_split(definition["layout"]["layers"], "alpha", "system")
    )
    return definition


def generate_split(layer_definitions, base_layout_name, target_layout_name):
    definitions = {
        f"{target_layout_name}L": {},
        f"{target_layout_name}R": {},
    }
    split_index = len(layer_definitions[base_layout_name]["keys"]) // 2
    target_color = layer_definitions[target_layout_name].get("leds", {}).get("RGB")

    # L side
    definitions[f"{target_layout_name}L"]["keys"] = (
        layer_definitions[base_layout_name]["keys"][:split_index]
        + layer_definitions[target_layout_name]["keys"][split_index:]
    )
    definitions[f"{target_layout_name}L"]["keys"][-2] = f"LY_TO({target_layout_name})"

    definitions[f"{target_layout_name}L"]["combos"] = {
        "chords": {
            k: v
            for k, v in layer_definitions[base_layout_name]["combos"]["chords"].items()
            if int(k.split("*")[0]) < split_index
        }
    }
    definitions[f"{target_layout_name}L"]["combos"]["chords"].update(
        {
            k: v
            for k, v in layer_definitions[target_layout_name]
            .get("combos", {})
            .get("chords", {})
            .items()
            if int(k.split("*")[0]) >= split_index
        }
    )

    if target_color:
        definitions[f"{target_layout_name}L"]["leds"] = {"RGB": target_color}

    # R side
    definitions[f"{target_layout_name}R"]["keys"] = (
        layer_definitions[target_layout_name]["keys"][:split_index]
        + layer_definitions[base_layout_name]["keys"][split_index:]
    )
    definitions[f"{target_layout_name}R"]["keys"][-2] = f"LY_TO({target_layout_name})"

    definitions[f"{target_layout_name}R"]["combos"] = {
        "chords": {
            k: v
            for k, v in layer_definitions[target_layout_name]
            .get("combos", {})
            .get("chords", {})
            .items()
            if int(k.split("*")[0]) < split_index
        }
    }
    definitions[f"{target_layout_name}R"]["combos"]["chords"].update(
        {
            k: v
            for k, v in layer_definitions[base_layout_name]["combos"]["chords"].items()
            if int(k.split("*")[0]) >= split_index
        }
    )

    if target_color:
        definitions[f"{target_layout_name}R"]["leds"] = {"RGB": target_color}

    return definitions


def main() -> None:
    logger.info("#" * 120)
    logger.info("# BOOTING")
    logger.info("#" * 120)

    definition = get_definition()

    # TODO: clean-up
    import storage

    if storage.getmount("/").label.endswith("R"):
        # if supervisor.runtime.usb_connected:
        from mymk.feature.keyboard import Keyboard
    else:
        from mymk.hardware.extension import Keyboard
    keyboard = Keyboard(definition)

    logger.info("#" * 120)
    logger.info("# ONLINE")
    logger.info("#" * 120 + "\n")

    keyboard.go(True)


if __name__ == "__main__":
    main()
