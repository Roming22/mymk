from seaks.action import Action
from seaks.controller import Controller
from seaks.event import Trigger
from seaks.hardware.board import Board
from seaks.state import StateMachine


class Keyboard:
    def __init__(self, rows: list, cols: list) -> None:
        Board(rows, cols)

        layers = StateMachine("layer", ["0", "1"])

        # Layer0
        keys_config = [("LEFT_SHIFT", False), ("A", True), ("B", True), ("C", True)]
        for switch, key_data in enumerate(keys_config):
            key_name, is_oneshot = key_data
            event_key = f"switch.{switch}"
            if is_oneshot:
                layers.states["0"].add_trigger(
                    Trigger(event_key, True), Action.oneshot(key_name)
                )
            else:
                layers.states["0"].add_trigger(
                    Trigger(event_key, True), Action.press(key_name)
                )
                layers.states["0"].add_trigger(
                    Trigger(event_key, False), Action.release(key_name)
                )

        # Layer1
        keys_config = [(None, True), ("D", True), ("E", True), ("F", True)]
        for switch, key_data in enumerate(keys_config):
            key, is_oneshot = key_data
            event_key = f"switch.{switch}"
            if is_oneshot:
                layers.states["1"].add_trigger(
                    Trigger(event_key, True), Action.oneshot(key)
                )
            else:
                layers.states["1"].add_trigger(
                    Trigger(event_key, True), Action.press(key)
                )
                layers.states["1"].add_trigger(
                    Trigger(event_key, False), Action.release(key)
                )

        # Left Shift
        lshift = StateMachine("left_shift", ["base", "locked", "ready-to-release"])
        lshift.states["base"].add_trigger(
            Trigger("layer.1", True), Action.state(lshift, "locked")
        )
        # Release the layer key while still holding the mod key
        lshift.states["locked"].add_trigger(
            Trigger("layer.1", False), Action.state(lshift, "base")
        )
        # Release the mod key while on the layer
        lshift.states["locked"].add_trigger(
            Trigger("switch.0", False), Action.state(lshift, "ready-to-release")
        )
        # Move back to base layer
        lshift.states["ready-to-release"].add_trigger(
            Trigger("layer.0", True),
            Action.state(lshift, "base"),
        )
        # Release shift key if was locker
        lshift.states["base"].add_trigger(
            Trigger("left_shift.ready-to-release", False),
            Action.release("LEFT_SHIFT"),
        )

        # Layer0/Layer1 transitions
        layers.states["0"].add_trigger(
            Trigger("switch.4", True),
            Action.state(layers, "1"),
        )
        layers.states["1"].add_trigger(
            Trigger("switch.4", False),
            Action.state(layers, "0"),
        )

    def go(self):
        while True:
            Controller.run()
