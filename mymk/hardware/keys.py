try:
    import usb_hid
    from adafruit_hid.keyboard import Keyboard as USB_Keyboard
    from adafruit_hid.keycode import Keycode

    _kbd = USB_Keyboard(usb_hid.devices)
except ModuleNotFoundError as ex:
    # Test mode
    import sys

    if "pytest" not in sys.modules:
        raise ex
    _kbd = None
    Keycode = None


_KC = {
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
    print("!!! PANIC !!!")
    _kbd.send(Keycode.MEH)


def press(key_name: str) -> callable:
    keycodes = get_keycodes_for(key_name)
    action = f"Press {key_name}"

    def func():
        print(action)
        for kc in keycodes:
            _kbd.press(getattr(Keycode, kc))

    # func.action = action
    return func


def release(key_name: str) -> callable:
    keycodes = get_keycodes_for(key_name)
    action = f"Release {key_name}"

    def func():
        print(action)
        for kc in reversed(keycodes):
            _kbd.release(getattr(Keycode, kc))

    # func.action = action
    return func
