import seaks.logic.action as action
import seaks.logic.event_handler as EventHandler
from seaks.utils.memory import memory_cost
from seaks.utils.toolbox import permutations

delay = [0.99]

combo_events = {}
current_combo = None


@memory_cost("Combos")
def load_combos(layer_uid: str, definitions: dict) -> None:
    reset_current_combo()
    print("Loading combos")
    if "sequences" not in definitions.keys():
        definitions["sequences"] = {}

    # Expand chords to sequences
    for chord, keycode in definitions.get("chords", {}).items():
        for sequence in permutations(chord.split("+")):
            sequence_id = "&".join(sequence)
            # Do not allow a chord to override a user defined sequence
            if sequence_id not in definitions["sequences"].keys():
                definitions["sequences"][sequence_id] = keycode

    # Load all sequences
    for sequence, keycode in definitions["sequences"].items():
        load_sequence(layer_uid, sequence.split("&"), keycode)

    print("Combo for:", list(combo_events.keys()))
    print("Combo for:", list(current_combo.keys()))


def load_sequence(layer_uid, sequence, keycode, prefix="") -> None:
    global current_combo
    print("Loading combo", prefix if prefix else "''", sequence, keycode)

    switch_id = sequence.pop(0)
    key_uid = f"{layer_uid}.switch.{switch_id}"
    release_event_id = f"!board.switch.{switch_id}"
    if prefix:
        combo_uid = f"{prefix}.{switch_id}"
    else:
        combo_uid = key_uid
    print("UID:", combo_uid)

    combo_timeout_event = f"{combo_uid}.combo.{'.'.join(sequence)}"

    # Timer to control the delay before the presses are not registered as a combo
    start_timer = action.start_timer(combo_timeout_event, delay[0])
    stop_timer = action.stop_timer(combo_timeout_event)

    clean_up = action.chain(
        stop_timer,
        reset_current_combo,
    )
    if len(sequence) == 0:
        print("Combo keycode:", keycode, "on", key_uid)
        on_press = action.chain(
            action.press(keycode),
            action.release(keycode),
            clean_up,
        )
    else:
        on_press = action.chain(
            lambda: load_sequence(layer_uid, list(sequence), keycode, combo_uid),
            lambda: add_action_for_event_id(combo_timeout_event, clean_up),
            # lambda: add_interrupt(clean_up),
            lambda: add_action_for_event_id(release_event_id, clean_up),
            start_timer,
        )
    add_action_for_event_id(key_uid, on_press)


def handle_event(event_id) -> None:
    global current_combo
    if event_id not in current_combo.keys():
        print("Not in a combo:", event_id, list(current_combo.keys()))
        return
    print("Combo found for: ", event_id, current_combo[event_id])
    for action in current_combo[event_id]:
        action()


def reset_current_combo() -> None:
    global current_combo
    print("Resetting combo")
    current_combo = combo_events

    print("Combo for:", list(combo_events.keys()))
    print("Combo for:", list(current_combo.keys()))


def new_current_combo() -> None:
    global current_combo
    print("Setting combo")
    current_combo = {}

    print("Combo for:", list(combo_events.keys()))
    print("Combo for:", list(current_combo.keys()))


def add_action_for_event_id(event_id, action) -> None:
    global current_combo
    print("Combo: Adding action for", event_id)
    if event_id not in current_combo.keys():
        current_combo[event_id] = [new_current_combo]
    current_combo[event_id].append(action)
