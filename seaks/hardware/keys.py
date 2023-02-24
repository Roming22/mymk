import usb_hid
from adafruit_hid.keyboard import Keyboard as USB_Keyboard
from adafruit_hid.keycode import Keycode

_kbd = USB_Keyboard(usb_hid.devices)


def get_keycode_for(key_name: str) -> Keycode:
    return getattr(Keycode, key_name)


def press(key_name: str) -> None:
    _kbd.press(get_keycode_for(key_name))


def release(key_name: str) -> None:
    _kbd.release(get_keycode_for(key_name))
