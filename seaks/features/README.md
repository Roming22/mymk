# Features

## Key

This is the simplest feature.
It outputs the given keycode when pressed, and releases it when the switch is released.

Example:
```
# 2x2 keyboard
definition = {
    "hardware": {
        "pins": {
            "cols": (board.D26, board.D22),
            "rows": (board.D6, board.D7),
        },
    },
    "layout": {"layers": OrderedDict()},
}
definition["layout"]["layers"]["WASD"] = {
    "keys": [
        "W", "A",
        "S", "D",
    ]
}
keyboard = Keyboard(definition)
```
The above definition will generate a keyboard that can output the `W`,`A`,`S` and `D` chararacters when pressed.

## Layers

Layers represent a which switches are assigned to which keys/actions.
Multiple layers can be defined for various purpose, with switches assigned for transitioning from one layer to another.
Layers can have transparent keys (by setting the key to None).
When the layer is activated the switch will inherit its key/action from the the previous layer.

There are 3 way to change layer:
* `LY_MO(layer_name)`: On switch press, activate `layer_name`. On switch release, deactivate the layer.
* `LY_TG(layer_name)`: On switch press, activate/deactivate `layer_name`. On switch release, do nothing.
* `LY_TO(layer_name)`: On switch press, activate `layer_name`. No action on switch release.

Example:
```
# 2x2 keyboard
definition = {
    "hardware": {
        "pins": {
            "cols": (board.D26, board.D22),
            "rows": (board.D6, board.D7),
        },
    },
    "layout": {"layers": OrderedDict()},
}
definition["layout"]["layers"]["nums"] = {
    "keys": [
        "LY_TG(fn)", "1",
        "2", "3",
    ]
}
definition["layout"]["layers"]["fn"] = {
    "keys": [
        None, "F1",
        "F2", "F3",
    ]
}
keyboard = Keyboard(definition)
```
The above definition will allow to use the same switches to output both numbers and Fn keys.
A transparent key was used to toggle between the layers.
Another valid way to flip flop between the layers would have been to use `LY_TO(fn)` on the `nums` layer and `LY_TO(nums)` on the `fn` layer.

It is currently not possible to combine `LY` keys with `TH` (TapHold) keys to make a switch that execute `LY_MO` on tap, but `LY_TO` or `LY_TG` on hold.

## TapHold

TapHold allows a switch to generate an action that depends on the time the switch was held down.
If the switch is released before a delay expires, the `tap` action is triggered.
If the switch is held down past the delay expiration, the `hold` action is triggered.

The default delay  is .5 seconds, but it can be set with:
```
from seaks.features.taphold import delay as taphold_delay

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
        "pins": {
            "cols": (board.D26, board.D22),
            "rows": (board.D6, board.D7),
        },
    },
    "layout": {"layers": OrderedDict()},
}
definition["layout"]["layers"]["alpha&sys"] = {
    "keys": [
"TH_HD(W, ESCACPE, 1.5)", "TH_HD(A, LEFT_SHIFT)",
"TH_TP(S, LEFT_CONTROL)", "TH_NO(D, ENTER)",
    ]
}
keyboard = Keyboard(definition)
```