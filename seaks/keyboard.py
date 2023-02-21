from time import sleep
import keypad

from adafruit_hid.keyboard import Keyboard as USB_Keyboard
from adafruit_hid.keycode import Keycode
import usb_hid

from seaks.action import Action
from seaks.event import Event
from seaks.event import Trigger
from seaks.state import StateMachine, State



class Keyboard:
    def __init__(self, rows: list, cols: list) -> None:
        self._km = keypad.KeyMatrix(
            row_pins=rows,
            column_pins=cols,
        )
        self.kbd = USB_Keyboard(usb_hid.devices)
        sm = StateMachine("keyboard")
        sm.new_state("base")

        oneshot = self.oneshot
        press = self.press
        release = self.release

        keys=[("LEFT_SHIFT", False), ("A", True), ("B", True), ("C", True), ("D", True), ("E", True)]
        for switch, key_data in enumerate(keys):
            key, is_oneshot = key_data
            event_key = f"key{switch}"
            if is_oneshot:
                sm.states["base"].add_trigger(Trigger(event_key, True), Action(oneshot(key)))
            else:
                sm.states["base"].add_trigger(Trigger(event_key, True), Action(press(key)))
                sm.states["base"].add_trigger(Trigger(event_key, False), Action(release(key)))

    def oneshot(self, key):
        kc = getattr(Keycode, key)
        def func():
            print(f"Press and release {key}")
            self.kbd.press(kc)
            self.kbd.release(kc)
            return True
        return func

    def press(self, key):
        kc = getattr(Keycode, key)
        def func():
            print(f"Press {key}")
            self.kbd.press(kc)
            return True
        return func

    def release(self, key):
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
