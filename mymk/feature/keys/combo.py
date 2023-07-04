"""This might need a complex parser

See the shunting yard algorithm.
"""

from mymk.hardware.keys import press, release
from mymk.logic.keys import loader_map
from mymk.logic.timer import Timer
from mymk.utils.logger import logger

# from mymk.utils.memory import memory_cost
from mymk.utils.toolbox import permutations

delay = 0.99


class Sequence:
    def __init__(self, switch_uids, delays, keycode: str) -> None:
        self.switch_uids = switch_uids
        self.delays = delays
        self.keycode = keycode
        self.pressed = False

    @classmethod
    def load(cls, universe, _: str, data: list[str]) -> None:
        switch_uids = []
        interlaced_data = []
        while data:
            switch_uids.append(data.pop(0))
            interlaced_data.append(data.pop(0))
        keycode = interlaced_data.pop(-1)
        delays = [float(x) for x in interlaced_data]
        delays.append(None)
        sequence = cls(switch_uids, delays, keycode)
        sequence.to_timeline_press_events(universe)

    def press(self) -> None:
        self.pressed = True
        press(self.keycode)()

    def release(self) -> None:
        if self.pressed is False:
            return
        self.pressed = False
        release(self.keycode)()

    def to_timeline_press_events(self, universe) -> None:
        combo_uid = f"{'+'.join([s.split('.')[-1] for s in self.switch_uids])}"
        timeline = universe.split(f"combo.{combo_uid}")

        sum_delay = 0
        sum_switch = []
        events = {
            self.switch_uids[1]: [],
        }
        for switch_uid, delay in zip(self.switch_uids, self.delays):
            if delay is not None:
                sum_delay += delay
                sum_switch.append(switch_uid.split(".")[-1])
                timer_name = f"timer.{combo_uid}.sequence.{'+'.join(sum_switch)}"
                timer = Timer(timer_name, sum_delay, universe, timeline)
                actions = []
                output = []
            else:
                actions = [
                    timeline.mark_determined,
                    lambda: self.to_timeline_release_events(universe),
                    timer.stop,
                ]
                output = [self.press]
            event = (switch_uid, actions, output)
            if switch_uid != self.switch_uids[0]:
                events[self.switch_uids[1]].append(event)

        timeline.events.update(events)

    def to_timeline_release_events(self, universe) -> None:
        timeline_events = {}

        for switch_uid in self.switch_uids:
            timeline_events[f"!{switch_uid}"] = [(switch_uid, [], [self.release])]
        universe.update_timeline(universe.current_timeline, timeline_events)


def load_combos(switch_prefix: str, combo_definitions: dict) -> list:
    sequences = {}
    for chord, keycode in combo_definitions.get("chords", {}).items():
        for sequence in expand_chord(chord):
            sequences[sequence] = keycode
    sequences.update(combo_definitions.get("sequences", {}))

    combos = []
    for sequence, keycode in sequences.items():
        combo = load_sequence(switch_prefix, sequence, keycode)
        combos.append(combo)
    return combos


def expand_chord(chord: str) -> list[str]:
    combo = chord.split("*")
    result = []
    for permutation in permutations(combo):
        result.append("+".join(permutation))
    return result


# @memory_cost("Sequence")
def load_sequence(switch_prefix: str, sequence: str, keycode: str) -> tuple:
    # logger.info("Loading %s", sequence)
    switch_uids = [
        f"{switch_prefix}.{switch_uid}" for switch_uid in sequence.split("+")
    ]
    delays = [delay for _ in switch_uids]
    delays[-1] = None
    combo_pairs = [
        f"{switch_uid},{delay if delay is not None else keycode}"
        for switch_uid, delay in zip(switch_uids, delays)
    ]
    combo_keycode = f"SQ({','.join(combo_pairs)})"
    result = (switch_uids[0], combo_keycode)
    return result


loader_map["SQ"] = Sequence.load
