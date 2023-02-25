import usb_hid
from adafruit_hid.keyboard import Keyboard as USB_Keyboard
from adafruit_hid.keycode import Keycode

_kbd = USB_Keyboard(usb_hid.devices)


def get_keycode_for(key_name: str) -> Keycode:
    return getattr(Keycode, key_name)


def oneshot(key_name: str):
    kc = get_keycode_for(key_name)

    def func():
        _kbd.press(kc)
        _kbd.release(kc)

    return func


def panic():
    print("!!! PANIC !!!")
    _kbd.send(Keycode.SPACE)


def press(key_name: str):
    kc = get_keycode_for(key_name)

    def func():
        _kbd.press(kc)

    return func


def release(key_name: str):
    kc = get_keycode_for(key_name)

    def func():
        _kbd.release(kc)

    return func
