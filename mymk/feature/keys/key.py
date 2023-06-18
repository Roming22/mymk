from mymk.hardware.keys import get_keycodes_for, press, release


class Key:
    loader_map = {}

    @classmethod
    def load(cls, switch_uid: str, keycode: str, universe) -> list[list[tuple]]:
        timelines_events = []
        if keycode in [None]:
            return timelines_events
        try:
            get_keycodes_for(keycode)
            cls.split_timeline(universe, switch_uid, keycode)
            return
        except AttributeError:
            pass
        loader_name, data = cls.parse_keycode(keycode)
        try:
            cls.loader_map[loader_name](universe, switch_uid, data)
        except KeyError:
            raise RuntimeError("Invalid keycode:", keycode)

    @staticmethod
    def create_timelines_events(universe, switch_uid, keycode) -> list[list[tuple]]:
        timeline_events = [
            {
                "what": f"{switch_uid} press/release",
                switch_uid: [
                    (switch_uid, [universe.mark_determined], [press(keycode)]),
                    (f"!{switch_uid}", [], [release(keycode)]),
                ],
            },
        ]
        return timeline_events

    @staticmethod
    def split_timeline(universe, switch_uid, keycode) -> None:
        timeline = universe.split(f"{switch_uid} press/release {keycode}")
        events = {f"!{switch_uid}": [(f"!{switch_uid}", [], [release(keycode)])]}
        timeline.events.update(events)
        timeline.output.append(press(keycode))
        timeline.mark_determined()

    @staticmethod
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
