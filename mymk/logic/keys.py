from mymk.hardware.keys import get_keycodes_for

loader_map = {}


def load(switch_uid: str, keycode: str, universe, debug=False) -> list[list[tuple]]:
    try:
        get_keycodes_for(keycode)
        loader_name, data = "KEY", keycode
    except AttributeError:
        loader_name, data = parse_keycode(keycode)
    try:
        loader_map[loader_name](universe, switch_uid, data)
    except KeyError:
        raise RuntimeError("Invalid keycode:", keycode)


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
