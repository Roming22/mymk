key_to_followup_actions = {}
key_to_action = {}

INTERRUPT = "interrupt"


def handle_event(event_id: str) -> None:
    for key_uid, k2a in key_to_followup_actions.items():
        if event_id in k2a.keys():
            # The action is responsible for setting
            # the new set of overrides if there are any.
            actions = key_to_followup_actions.pop(key_uid)
            actions[event_id]()
            return
    if event_id in key_to_action.keys():
        key_to_action[event_id]()


def has_interrupted(event_id: str) -> bool:
    if not key_to_followup_actions:
        return False
    if event_id in []:
        return False
    handle_event(INTERRUPT)
    return True


def followup_actions_for(key_uid: str, key_to_action) -> "Callable":
    def func():
        key_to_followup_actions[key_uid] = key_to_action

    return func
