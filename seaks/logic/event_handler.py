from seaks.features.key import get_actions_for
from seaks.features.layer import ActiveLayer

event_to_followup_actions = {}
INTERRUPT = "interrupt"


def handle_event(event_id: str) -> None:
    for event_uid, k2a in event_to_followup_actions.items():
        if event_id in k2a.keys():
            # The action is responsible for setting
            # the new set of overrides if there are any.
            print(event_id, event_uid)
            actions = event_to_followup_actions.pop(event_uid)
            actions[event_id]()
            return

    keycode = ActiveLayer.get_keycode(event_id)
    print(keycode)
    handle_keycode(event_id, keycode)


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
