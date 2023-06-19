import sys
from unittest.mock import MagicMock

####################################################################################################
# Mock all the RPI modules
####################################################################################################


# adafruit_hid
adafruit_hid = type(sys)("adafruit_hid")
sys.modules["adafruit_hid"] = adafruit_hid


# adafruit_hid.keyboard
adafruit_hid.keyboard = type(sys)("keyboard")
adafruit_hid.keyboard.Keyboard = MagicMock()
sys.modules["adafruit_hid.keyboard"] = adafruit_hid.keyboard


# adafruit_hid.keycode
class Keycode:
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"
    H = "H"
    I = "I"
    J = "J"
    K = "K"
    L = "L"
    M = "M"
    N = "N"
    O = "O"
    P = "P"
    Q = "Q"
    R = "R"
    S = "S"
    T = "T"
    U = "U"
    V = "V"
    W = "W"
    X = "X"
    Y = "Y"
    Z = "Z"

    ONE = "ONE"
    TWO = "TWO"
    THREE = "THREE"
    FOUR = "FOUR"
    FIVE = "FIVE"
    SIX = "SIX"
    SEVEN = "SEVEN"
    EIGHT = "EIGHT"
    NINE = "NINE"
    ZERO = "ZERO"
    ENTER = "ENTER"
    RETURN = "RETURN"
    ESCAPE = "ESCAPE"
    BACKSPACE = "BACKSPACE"
    TAB = "TAB"
    SPACEBAR = "SPACEBAR"
    SPACE = "SPACE"
    MINUS = "MINUS"
    EQUALS = "EQUALS"
    LEFT_BRACKET = "LEFT_BRACKET"
    RIGHT_BRACKET = "RIGHT_BRACKET"
    BACKSLASH = "BACKSLASH"
    POUND = "POUND"
    SEMICOLON = "SEMICOLON"
    QUOTE = "QUOTE"
    GRAVE_ACCENT = "GRAVE_ACCENT"
    COMMA = "COMMA"
    PERIOD = "PERIOD"
    FORWARD_SLASH = "FORWARD_SLASH"

    CAPS_LOCK = "CAPS_LOCK"

    F1 = "F1"
    F2 = "F2"
    F3 = "F3"
    F4 = "F4"
    F5 = "F5"
    F6 = "F6"
    F7 = "F7"
    F8 = "F8"
    F9 = "F9"
    F10 = "F10"
    F11 = "F11"
    F12 = "F12"

    PRINT_SCREEN = "PRINT_SCREEN"
    SCROLL_LOCK = "SCROLL_LOCK"
    PAUSE = "PAUSE"

    INSERT = "INSERT"
    HOME = "HOME"
    PAGE_UP = "PAGE_UP"
    DELETE = "DELETE"
    END = "END"
    PAGE_DOWN = "PAGE_DOWN"

    RIGHT_ARROW = "RIGHT_ARROW"
    LEFT_ARROW = "LEFT_ARROW"
    DOWN_ARROW = "DOWN_ARROW"
    UP_ARROW = "UP_ARROW"

    KEYPAD_NUMLOCK = "KEYPAD_NUMLOCK"
    KEYPAD_FORWARD_SLASH = "KEYPAD_FORWARD_SLASH"
    KEYPAD_ASTERISK = "KEYPAD_ASTERISK"
    KEYPAD_MINUS = "KEYPAD_MINUS"
    KEYPAD_PLUS = "KEYPAD_PLUS"
    KEYPAD_ENTER = "KEYPAD_ENTER"
    KEYPAD_ONE = "KEYPAD_ONE"
    KEYPAD_TWO = "KEYPAD_TWO"
    KEYPAD_THREE = "KEYPAD_THREE"
    KEYPAD_FOUR = "KEYPAD_FOUR"
    KEYPAD_FIVE = "KEYPAD_FIVE"
    KEYPAD_SIX = "KEYPAD_SIX"
    KEYPAD_SEVEN = "KEYPAD_SEVEN"
    KEYPAD_EIGHT = "KEYPAD_EIGHT"
    KEYPAD_NINE = "KEYPAD_NINE"
    KEYPAD_ZERO = "KEYPAD_ZERO"
    KEYPAD_PERIOD = "KEYPAD_PERIOD"
    KEYPAD_BACKSLASH = "KEYPAD_BACKSLASH"

    APPLICATION = "APPLICATION"
    POWER = "POWER"
    KEYPAD_EQUALS = "KEYPAD_EQUALS"
    F13 = "F13"
    F14 = "F14"
    F15 = "F15"
    F16 = "F16"
    F17 = "F17"
    F18 = "F18"
    F19 = "F19"
    F20 = "F20"
    F21 = "F21"
    F22 = "F22"
    F23 = "F23"
    F24 = "F24"

    LEFT_CONTROL = "LEFT_CONTROL"
    CONTROL = "CONTROL"
    LEFT_SHIFT = "LEFT_SHIFT"
    SHIFT = "SHIFT"
    LEFT_ALT = "LEFT_ALT"
    ALT = "ALT"
    OPTION = "OPTION"
    LEFT_GUI = "LEFT_GUI"
    RIGHT_CONTROL = "RIGHT_CONTROL"
    RIGHT_SHIFT = "RIGHT_SHIFT"
    RIGHT_ALT = "RIGHT_ALT"
    RIGHT_GUI = "RIGHT_GUI"


adafruit_hid.keycode = type(sys)("keycode")
adafruit_hid.keycode.Keycode = Keycode
sys.modules["adafruit_hid.keycode"] = adafruit_hid.keycode


# Board
module = MagicMock()
sys.modules["board"] = module


# Keypad
module = type(sys)("keypad")
module.KeyMatrix = MagicMock(return_value=[])
sys.modules["keypad"] = module


# Neopixels
module = type(sys)("neopixel")
module.NeoPixel = MagicMock()
sys.modules["neopixel"] = module

# Storage
module = type(sys)("storage")
module.getmount = MagicMock(return_value=MagicMock(label="KEYBOARD-L"))
sys.modules["storage"] = module

# Supervisor
module = type(sys)("supervisor")
module.runtime = MagicMock(
    return_value=MagicMock(serial_connected=True, usb_connected=True)
)
sys.modules["supervisor"] = module

# usb_hid
module = type(sys)("usb_hid")
module.devices = None
sys.modules["usb_hid"] = module
