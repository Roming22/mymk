import time

from seaks.features.combo import handle_event as combo_handle_event
from seaks.features.key import get_actions_for
from seaks.features.layer import ActiveLayer
from seaks.logic.timer import Timer
from seaks.utils.memory import get_usage as get_memory_usage
from seaks.utils.time import pretty_print

event_to_followup_actions = {}
INTERRUPT = "interrupt"

time_last_event = time.monotonic_ns()


def handle_event(event_id: str) -> None:
    global time_last_event
    print(get_memory_usage(True))
    print(f"\n# {event_id} {'#' * 100}"[:100])
    now = time.monotonic_ns()
    print("# At:", pretty_print(now), f"(+{(now-time_last_event)/10**6}ms)")
    Timer.now = now

    combo_handle_event(event_id)

    for event_uid, k2a in event_to_followup_actions.items():
        if event_id in k2a.keys():
            # The action is responsible for setting
            # the new set of overrides if there are any.
            print(event_id, event_uid)
            actions = event_to_followup_actions.pop(event_uid)
            actions[event_id]()
            time_last_event = now
            print(f"# Processed in {(time.monotonic_ns()-now)/10**6}ms")
            print(get_memory_usage(True))
            return

    keycode = ActiveLayer.get_keycode(event_id)
    print(keycode)
    handle_keycode(event_id, keycode)
    time_last_event = now
    print(f"# Processed in {(time.monotonic_ns()-now)/10**6}ms")
    print(get_memory_usage(True))


def has_interrupted(event_id: str) -> bool:
    if not event_to_followup_actions:
        return False
    if event_id in []:
        return False
    handle_event(INTERRUPT)
    return True


def handle_keycode(key_uid, keycode):
    switch_uid = ".".join(key_uid.split(".")[-2:])
    release_event_id = f"!board.{switch_uid}"

    on_press_action, on_release_action, on_interrupt_action = get_actions_for(
        key_uid, keycode
    )
    event_to_followup_actions[switch_uid] = {
        release_event_id: on_release_action,
    }
    if on_interrupt_action:
        print("adding interrupt to", switch_uid, on_interrupt_action)
        event_to_followup_actions[switch_uid][INTERRUPT] = on_interrupt_action

    on_press_action()
