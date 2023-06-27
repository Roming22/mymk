# Features

## Key

This is the simplest feature.
It outputs the given keycode when pressed, and releases it when the switch is released.

Example:
```
# 2x2 keyboard
definition = {
    "hardware": {
        "myboard": {
            "pins": {
                "cols": (board.D26, board.D22),
                "rows": (board.D6, board.D7),
            },
        },
    },
    "layout": {
        "layers": {
            "WASD": {
                "keys": [
                    "W", "A",
                    "S", "D",
                ],
            },
        },
    },
    "settings": {
        "default_layer": "WASD",
    },
}
keyboard = Keyboard(definition)
```
The above definition will generate a keyboard that can output the `W`,`A`,`S` and `D` chararacters when pressed.

## Layers

Layers represent a which switches are assigned to which keys/actions.
Multiple layers can be defined for various purpose, with switches assigned for transitioning from one layer to another.
Layers can have transparent keys (by setting the key to None).
When the layer is activated the switch will inherit its key/action from the the previous layer.

There are 2 way to change layer:
* `LY_MO(layer_name)`: On switch press, activate `layer_name`. On switch release, deactivate the layer.
* `LY_TO(layer_name)`: On switch press, activate `layer_name`. No action on switch release.

Example:
```
# 2x2 keyboard
definition = {
    "hardware": {
        "myboard": {
            "pins": {
                "cols": (board.D26, board.D22),
                "rows": (board.D6, board.D7),
            },
        },
    },
    "layout": {
        "layers": {
            "nums": {
                "keys": [
                    "LY_TO(fn)", "1",
                    "2", "3",
                ],
            },
            "fn": {
                "keys": [
                    "LY_TO(nums)", "F1",
                    "F2", "F3",
                ],
            },
        },
    },
    "settings": {
        "default_layer": "nums",
    },
}
keyboard = Keyboard(definition)
```
The above definition will allow to use the same switches to output both numbers and Fn keys.
`LY_TO` is used to flip flop between the layers.

## TapHold

TapHold allows a switch to generate an action that depends on the time the switch was held down.
If the switch is released before a delay expires, the `tap` action is triggered.
If the switch is held down past the delay expiration, the `hold` action is triggered.

The default delay  is .3 seconds, but it can be set with:
```
from mymk.features.taphold import delay as taphold_delay

# Set to 2 seconds
taphold_delay[0] = 2
```

There are 3 ways to declare a TapHold switch:
* `TH_HD(tap_action, hold_action)`: `tap_action` on tap, `hold_action` on release or if another input interrupts the TapHold.
* `TH_NO(tap_action, hold_action)`: `tap_action` on tap, `hold_action` on release, do nothing if another input interrupts the TapHold.
* `TH_TP(tap_action, hold_action)`: `tap_action` on tap or if another input interrupts the TapHold, `hold_action` on release.

The delay can also be set per switch by adding the value in second as third argument.

Example:
```
# 2x2 keyboard
definition = {
    "hardware": {
        "myboard": {
            "pins": {
                "cols": (board.D26, board.D22),
                "rows": (board.D6, board.D7),
            },
        },
    },
    "layout": {
        "layers": {
            "alpha&sys": {
                "keys": [
    "TH_HD(W, ESCAPE, 1.5)",  "TH_HD(A, LEFT_SHIFT)",
    "TH_TP(S, LEFT_CONTROL)", "TH_NO(D, ENTER)",
                ],
            },
        },
    },
    "settings": {
        "default_layer": "alpha&sys",
    },
}
keyboard = Keyboard(definition)
```

## MultiTap

MultiTap is a special key mode that changes the output based on the number of times a key is quickly pressed in succession.
A MultiTap key is declared using the `MT(arg1, arg2, ..., argN)` function, where the argument at position N specifies the action to be taken when the key is pressed N times.
If the last agrument is reached, the last action is executed and the command circles back to the first argument.

Example:
```
# 2x2 keyboard
definition = {
    "hardware": {
        "myboard": {
            "pins": {
                "cols": (board.D26, board.D22),
                "rows": (board.D6, board.D7),
            },
        },
    },
    "layout": {
        "layers": {
            "alpha&sys": {
                "keys": [
    "MT(A)",            "MT(B,C)",
    "MT(D,LY_TO(fn))",  "MT(E, TH_HD(F, LEFT_SHIFT),TH_HD(ESCAPE, LEFT_CONTROL), ENTER)",
                ],
            },
            "fn": {
                "keys": [
                    "LY_TO(alpha&sys)",     "MT(F1, F2, F3, F4)",
                    "MT(F5, F6, F7, F8)"    "MT(F9, F10, F11, F12)",
                ],
            },
        },
    },
    "settings": {
        "default_layer": "alpha&sys",
    },
}
keyboard = Keyboard(definition)
```

In the above example:
* `MT(A)` is the same as `A`. This syntax is valid but useless.
* `MT(B,C)` will output `b` if pressed once, or `c` if pressed twice. It will output `cb` if pressed three times rapidly. To output `bc`, pause shortly after the first keystroke.
* `MT(D,LY_TO(fn))` shows that commands can be nested.
* `MT(E, TH_HD(F, LEFT_SHIFT),TH_HD(ESCAPE, LEFT_CONTROL), ENTER)` is a complex example of a 4-MultiTap, demonstrating the use of TapHold within the multitap.

## Combos

There are two types of combos:
* chords: the switches can be pressed in any order. The delimiter is '*'.
* sequences: the switches must be pressed in the right order. The delimiter is '+'.

All keys of the combos must be pressed for the combo to trigger.
I.e. if a key belonging to a combo is released while the combo is being keyed, the combo will be cancelled.

If a chord conflicts with a sequence, the sequence takes priority.
For example if the chord `1*2*3` is assigned to `ENTER` and the sequence `3+2+1` is assigned to `SPACE`:
* `1+2+3`, `1+3+2`, `2+1+3`, `2+3+1`, `3+1+2` will output `ENTER`
* `3+2+1` will output `SPACE`

Example
```
# 2x2 keyboard
definition = {
    "hardware": {
        "myboard": {
            "pins": {
                "cols": (board.D26, board.D22),
                "rows": (board.D6, board.D7),
            },
        },
    },
    "layout": {
        "layers": {
            "alpha&sys": {
                "keys": [
    "TH_HD(W, ESCACPE, 1.5)", "TH_HD(A, LEFT_SHIFT)",
    "TH_TP(S, LEFT_CONTROL)", "TH_NO(D, ENTER)",
                ],
                "combos": {
                    "chords": {
                        "0*1": "F1",
                        "2*3": "F2",
                    },
                    "sequences": {
                        "0+3": "DOWN",
                        "3+0" :"UP",
                    },
                },
            },
        },
    },
    "settings": {
        "default_layer": "alpha&sys",
    },
}
keyboard = Keyboard(definition)
```
