import adafruit_hid.keyboard
import usb_hid
from adafruit_hid.keycode import Keycode

from mymk.utils.logger import logger

_kbd = adafruit_hid.keyboard.Keyboard(usb_hid.devices)

_KC = {
    "0": "ZERO",
    "1": "ONE",
    "2": "TWO",
    "3": "THREE",
    "4": "FOUR",
    "5": "FIVE",
    "6": "SIX",
    "7": "SEVEN",
    "8": "EIGHT",
    "9": "NINE",
    "DOLLAR": ["LEFT_SHIFT", "FOUR"],
    "DOT": "PERIOD",
    "EQUAL": "EQUALS",
    "ESC": "ESCAPE",
    "EXCLAIM": ["LEFT_SHIFT", "ONE"],
    "GRAVE": "GRAVE_ACCENT",
    "HASH": ["LEFT_SHIFT", "THREE"],
    "LALT": "LEFT_ALT",
    "LCTL": "LEFT_CONTROL",
    "LGUI": "LEFT_GUI",
    "LSFT": "LEFT_SHIFT",
    "MEH": ["LEFT_ALT", "LEFT_CONTROL", "LEFT_SHIFT"],
    "NO": [],
    "RALT": "RIGHT_ALT",
    "RCTL": "RIGHT_CONTROL",
    "RGUI": "RIGHT_GUI",
    "RSFT": "RIGHT_SHIFT",
    "SLASH": "FORWARD_SLASH",
    "UNDERSCORE": ["LEFT_SHIFT", "MINUS"],
}


def get_keycodes_for(keycode: str) -> list[Keycode]:
    if keycode in _KC.keys():
        keycodes = _KC[keycode]
        if not isinstance(keycodes, list):
            keycodes = [keycodes]
    else:
        keycodes = [keycode]
    # Check all keycodes are valid
    [getattr(Keycode, kc) for kc in keycodes]
    return keycodes


def panic():
    logger.info("!!! PANIC !!!")
    _kbd.send(Keycode.MEH)


def press(key_name: str) -> callable:
    keycodes = get_keycodes_for(key_name)
    action = f"Press {key_name}"

    def func():
        logger.info(action)
        for kc in keycodes:
            _kbd.press(getattr(Keycode, kc))

    # func.action = action
    return func


def release(key_name: str) -> callable:
    keycodes = get_keycodes_for(key_name)
    action = f"Release {key_name}"

    def func():
        logger.info(action)
        for kc in reversed(keycodes):
            _kbd.release(getattr(Keycode, kc))

    # func.action = action
    return func
