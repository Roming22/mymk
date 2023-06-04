"""This might need a complex parser

See the shunting yard algorithm.
"""

from mymk.feature.keys.key import Key
from mymk.hardware.keys import press, release
from mymk.logic.action import chain
from mymk.logic.timer import Timer
from mymk.utils.memory import memory_cost
from mymk.utils.toolbox import permutations

delay = 0.99


class Sequence:
    def __init__(self, switch_uids, delays, keycode: str) -> None:
        self.switch_uids = switch_uids
        self.delays = delays
        self.keycode = keycode
        self.pressed = False

    @classmethod
    def load(cls, universe, switch_uid: str, data):
        switch_uids = []
        interlaced_data = []
        while data:
            switch_uids.append(data.pop(0))
            interlaced_data.append(data.pop(0))
        keycode = interlaced_data.pop(-1)
        delays = [float(x) for x in interlaced_data]
        delays.append(None)
        sequence = cls(switch_uids, delays, keycode)
        return sequence.to_timeline_press_events(universe)

    def press(self) -> None:
        self.pressed = True
        press(self.keycode)()

    def release(self) -> None:
        if self.pressed is False:
            return
        self.pressed = False
        release(self.keycode)()

    def to_timeline_press_events(self, universe):
        timeline_events = []

        timer_name = f"timer.{'.'.join(self.switch_uids)}.sequence"
        timer = Timer(timer_name, self.delays[0], universe)

        for switch_uid, delay in zip(self.switch_uids, self.delays):
            if delay is not None:
                action = timer.start
                output = None
            else:
                action = chain(
                    universe.mark_determined,
                    lambda: self.to_timeline_release_events(universe),
                    timer.stop,
                )
                output = self.press
            event = (switch_uid, action, output)
            timeline_events.append(event)
        return [{self.switch_uids[0]: timeline_events}]

    def to_timeline_release_events(self, universe):
        timeline_events = {}

        for switch_uid in self.switch_uids:
            timeline_events[f"!{switch_uid}"] = [(switch_uid, None, self.release)]
        universe.update_timeline(universe.current_timeline, timeline_events)


@memory_cost("Combo")
def load_combo(switch_prefix: str, definition: str, keycode: str) -> list:
    switch_to_keycodes = []
    for combo in expand_combo(definition):
        print("Loading", combo)
        switch_uids = [
            f"{switch_prefix}.{switch_uid}" for switch_uid in combo.split("+")
        ]
        delays = [delay for _ in switch_uids]
        delays[-1] = None
        combo_pairs = [
            f"{switch_uid},{delay if delay is not None else keycode}"
            for switch_uid, delay in zip(switch_uids, delays)
        ]
        combo_keycode = f"SQ({','.join(combo_pairs)})"
        switch_to_keycodes.append((switch_uids[0], combo_keycode))
    return switch_to_keycodes


def expand_combo(definition: str) -> list:
    combos = []
    print(definition)
    return [definition]


# def _tokenize_groups(definition) -> list:
#     return definition


def _tokenize_or(definition) -> list:
    tokens = definition.split("|")
    return tokens


def _tokenize_and(definition) -> list:
    return [definition]


def _tokenize_star(definition) -> list:
    combos = []
    tokens = definition.split("*")
    for sequence in permutations(tokens):
        combos += ["+".join(sequence)]
    return combos


Key.loader_map["SQ"] = Sequence.load
