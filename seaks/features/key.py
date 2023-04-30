import re

import seaks.logic.action as action
import seaks.logic.event_handler as EventHandler
from seaks.hardware.keys import get_keycodes_for
from seaks.utils.memory import memory_cost

action_func = {}


def get_actions_for(key_uid: str, keycode: str):
    try:
        if keycode in ["NO", None] or get_keycodes_for(keycode):
            func = get_keycode_actions
            args = [keycode]
    except AttributeError:
        if "(" in keycode and keycode.endswith(")"):
            func_name, args = parse_keycode(keycode)
            try:
                func = action_func[func_name]
            except KeyError:
                raise RuntimeError("Keycode not implemented:", func_name)
        else:
            raise RuntimeError(f"Keycode not implemented: '{keycode}'")
    return func(key_uid, *args)


def get_keycode_actions(_, keycode: str):
    on_press = action.press(keycode)
    on_release = action.release(keycode)
    on_interrupt = None
    return (on_press, on_release, on_interrupt)


def parse_keycode(keycode: str) -> tuple[str, list[str]]:
    left_parenthesis = keycode.index("(")
    func_name = keycode[:left_parenthesis]
    args_str = keycode[left_parenthesis + 1 : -1]

    # Initialize an empty list to store the output
    output_list: list[str] = []
    # Initialize a variable to keep track of the current substring
    current_substring: str = ""
    # Initialize a variable to keep track of the number of open parentheses
    open_parentheses: int = 0

    # Loop through each character in the input string
    for char in args_str:
        # If the current character is an open parenthesis, increment the count
        if char == "(":
            open_parentheses += 1
        # If the current character is a close parenthesis, decrement the count
        elif char == ")":
            open_parentheses -= 1

        # If the current character is a comma and there are no open parentheses,
        # append the current substring to the output list and reset it to an empty string
        if char == "," and open_parentheses == 0:
            output_list.append(current_substring.strip())
            current_substring = ""
        else:
            current_substring += char

    # Append the last substring to the output list
    output_list.append(current_substring.strip())

    return (func_name, output_list)
