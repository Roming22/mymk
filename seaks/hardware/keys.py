import usb_hid
from adafruit_hid.keyboard import Keyboard as USB_Keyboard
from adafruit_hid.keycode import Keycode

_kbd = USB_Keyboard(usb_hid.devices)

_KC = {
    "DOLLAR": ["LEFT_SHIFT", "FOUR"],
    "DOT": "PERIOD",
    "EQUAL": "EQUALS",
    "ESC": "ESCAPE",
    "EXCLAIM": ["LEFT_SHIFT", "ONE"],
    "GRAVE": "GRAVE_ACCENT",
    "HASH": ["LEFT_SHIFT", "THREE"],
    "LGUI": "LEFT_GUI",
    "MEH": ["LEFT_SHIFT", "LEFT_CONTROL", "LEFT_ALT"],
    "NO": None,
    "RGUI": "RIGHT_GUI",
    "SLASH": "FORWARD_SLASH",
    "UNDERSCORE": ["LEFT_SHIFT", "MINUS"],
}


def get_keycodes_for(keycode: str) -> list[Keycode]:
    if keycode in _KC.keys():
        keycode = _KC[keycode]
    if not isinstance(keycode, list):
        keycode = [keycode]
    return [getattr(Keycode, kc) for kc in keycode]


def oneshot(key_name: str) -> None:
    print(f"Oneshot {key_name}")
    keycodes = get_keycodes_for(key_name)
    for kc in keycodes:
        _kbd.press(kc)
    for kc in keycodes:
        _kbd.release(kc)


def panic():
    print("!!! PANIC !!!")
    _kbd.send(Keycode.MEH)


def press(key_name: str) -> None:
    print(f"Press {key_name}")
    keycodes = get_keycodes_for(key_name)
    for kc in keycodes:
        _kbd.press(kc)


def release(key_name: str) -> None:
    print(f"Release {key_name}")
    keycodes = get_keycodes_for(key_name)
    for kc in keycodes:
        _kbd.release(kc)
