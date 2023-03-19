from seaks.features.key import instances as key_instances
from seaks.logic.event import Timer
from seaks.utils.memory import check_memory
from seaks.utils.toolbox import permutations


class Sequence:
    @check_memory("Sequence")
    def __init__(self, keys: list[tuple[str, str]], keycode: str, delay: float) -> None:
        keycode = str.upper(keycode)
        print("Setup", keycode)

        combo_name = (
            ".".join([f"{layer}.switch.{switch}" for layer, switch in keys])
            + ".timer.combo"
        )
        self.name = combo_name
        self.keycode = keycode
        print(f"Sequence: {combo_name}")

        # Timer to control the hold delay
        self.timer = Timer(combo_name, delay)

        # Add to first key
        first_key_uid = f"{keys[0][0]}.switch.{keys[0][1]}"
        key_instances[first_key_uid].combos.append(self)


class Chord:
    @check_memory("Chord")
    def __init__(self, keys: list[str], key_name: str) -> None:
        keys = [str.upper(k) for k in keys]
        key_name = str.upper(key_name)
        for event_sequence in permutations(keys):
            Sequence(event_sequence, key_name)
