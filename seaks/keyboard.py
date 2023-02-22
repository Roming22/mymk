import keypad
import usb_hid
from adafruit_hid.keyboard import Keyboard as USB_Keyboard

from seaks.action import Action
from seaks.event import Trigger
from seaks.state import StateMachine


class Keyboard:
    def __init__(self, rows: list, cols: list) -> None:
        self._km = keypad.KeyMatrix(
            row_pins=rows,
            column_pins=cols,
        )
        kbd = USB_Keyboard(usb_hid.devices)
        keys = StateMachine("keyboard")
        keys.new_state("base")
        keys.new_state("layer1")
        keys.activate_state(keys.states["base"])

        lshift = StateMachine("LeftShift")
        for state in ["base", "locked", "ready-to-release"]:
            lshift.new_state(state)
        lshift.activate_state(lshift.states["base"])

        # Layer0
        keys_config = [("LEFT_SHIFT", False), ("A", True), ("B", True), ("C", True)]
        for switch, key_data in enumerate(keys_config):
            key, is_oneshot = key_data
            event_key = f"key.{switch}"
            if is_oneshot:
                keys.states["base"].add_trigger(
                    Trigger(event_key, True), Action.oneshot(kbd, key)
                )
            else:
                keys.states["base"].add_trigger(
                    Trigger(event_key, True), Action.press(kbd, key)
                )
                keys.states["base"].add_trigger(
                    Trigger(event_key, False), Action.release(kbd, key)
                )

        # Layer1
        keys_config = [(None, True), ("D", True), ("E", True), ("F", True)]
        for switch, key_data in enumerate(keys_config):
            key, is_oneshot = key_data
            event_key = f"key.{switch}"
            if is_oneshot:
                keys.states["layer1"].add_trigger(
                    Trigger(event_key, True), Action.oneshot(kbd, key)
                )
            else:
                keys.states["layer1"].add_trigger(
                    Trigger(event_key, True), Action.press(kbd, key)
                )
                keys.states["layer1"].add_trigger(
                    Trigger(event_key, False), Action.release(kbd, key)
                )

        # Left Shift
        lshift.states["base"].add_trigger(
            Trigger("keyboard.layer1", True), Action.state(lshift, "locked")
        )
        # Release the layer key while still holding the mod key
        lshift.states["locked"].add_trigger(
            Trigger("keyboard.layer1", False), Action.state(lshift, "base")
        )
        # Release the mod key while on the layer
        lshift.states["locked"].add_trigger(
            Trigger("key.0", False), Action.state(lshift, "ready-to-release")
        )
        # Move back to base layer
        lshift.states["ready-to-release"].add_trigger(
            Trigger("keyboard.layer1", False),
            Action.state(lshift, "base"),
        )
        # Release shift key if was locker
        lshift.states["base"].add_trigger(
            Trigger("LeftShift.ready-to-release", False),
            Action.release(kbd, "LEFT_SHIFT"),
        )

        # Layer0/Layer1 transitions
        keys.states["base"].add_trigger(
            Trigger("key.4", True),
            Action.state(keys, "layer1"),
        )
        keys.states["layer1"].add_trigger(
            Trigger("key.4", False),
            Action.state(keys, "base"),
        )

    def get_events(self):
        if event := self._km.events.get():
            Trigger(f"key.{event.key_number}", event.pressed).fire()

    def go(self):
        while True:
            self.get_events()
            StateMachine.process_events()
