from time import sleep

import keypad
import usb_hid
from adafruit_hid.keyboard import Keyboard as USB_Keyboard
from adafruit_hid.keycode import Keycode

from seaks.action import Action, noop
from seaks.event import Event, Trigger
from seaks.state import State, StateMachine


class Keyboard:
    def __init__(self, rows: list, cols: list) -> None:
        self._km = keypad.KeyMatrix(
            row_pins=rows,
            column_pins=cols,
        )
        self.kbd = USB_Keyboard(usb_hid.devices)
        keys = StateMachine("keyboard")
        keys.new_state("base")
        keys.new_state("layer1")

        lshift = StateMachine("LeftShift")
        for state in ["base", "locked", "ready-to-release"]:
            lshift.new_state(state)

        oneshot = self.oneshot
        press = self.press
        release = self.release

        # Layer0
        keys_config = [("LEFT_SHIFT", False), ("A", True), ("B", True), ("C", True)]
        for switch, key_data in enumerate(keys_config):
            key, is_oneshot = key_data
            event_key = f"key{switch}"
            if is_oneshot:
                keys.states["base"].add_trigger(
                    Trigger(event_key, True), Action(oneshot(key))
                )
            else:
                keys.states["base"].add_trigger(
                    Trigger(event_key, True), Action(press(key))
                )
                keys.states["base"].add_trigger(
                    Trigger(event_key, False), Action(release(key))
                )

        # Layer1
        keys_config = [(None, True), ("D", True), ("E", True), ("F", True)]
        for switch, key_data in enumerate(keys_config):
            key, is_oneshot = key_data
            event_key = f"key{switch}"
            if is_oneshot:
                keys.states["layer1"].add_trigger(
                    Trigger(event_key, True), Action(oneshot(key))
                )
            else:
                keys.states["layer1"].add_trigger(
                    Trigger(event_key, True), Action(press(key))
                )
                keys.states["layer1"].add_trigger(
                    Trigger(event_key, False), Action(release(key))
                )

        # Left Shift
        lshift.states["base"].add_trigger(
            Trigger("layer1", True), Action.noop, lshift.states["locked"]
        )
        lshift.states["locked"].add_trigger(
            Trigger("layer1", False), Action.noop, lshift.states["base"]
        )
        lshift.states["locked"].add_trigger(
            Trigger("key1", False), Action.noop, lshift.states["ready-to-release"]
        )
        lshift.states["ready-to-release"].add_trigger(
            Trigger("layer1", False),
            Action(release("LEFT_SHIFT")),
            lshift.states["base"],
        )

        # Layer0/Layer1 transitions
        keys.states["base"].add_trigger(
            Trigger("key4", True),
            Action(Trigger("layer1", True).fire),
            keys.states["layer1"],
        )
        keys.states["layer1"].add_trigger(
            Trigger("key4", False),
            Action(Trigger("layer1", False).fire),
            keys.states["base"],
        )

    def oneshot(self, key):
        if key is None:
            return noop

        kc = getattr(Keycode, key)

        def func():
            print(f"Press and release {key}")
            self.kbd.press(kc)
            self.kbd.release(kc)
            return True

        return func

    def press(self, key):
        if key is None:
            return noop

        kc = getattr(Keycode, key)

        def func():
            print(f"Press {key}")
            self.kbd.press(kc)
            return True

        return func

    def release(self, key):
        if key is None:
            return noop

        kc = getattr(Keycode, key)

        def func():
            print(f"Release {key}")
            self.kbd.release(kc)
            return True

        return func

    def get_events(self):
        while True:
            if base_event := self._km.events.get():
                event = Event.notify(
                    f"key{base_event.key_number}",
                    base_event.pressed,
                    base_event.timestamp,
                )
