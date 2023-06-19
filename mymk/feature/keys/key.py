from mymk.hardware.keys import press, release
from mymk.logic.keys import loader_map


def load_key(universe, switch_uid, keycode) -> None:
    timeline = universe.split(f"{switch_uid} press/release {keycode}")
    events = {f"!{switch_uid}": [(f"!{switch_uid}", [], [release(keycode)])]}
    timeline.events.update(events)
    timeline.output.append(press(keycode))
    timeline.mark_determined()


loader_map["KEY"] = load_key
