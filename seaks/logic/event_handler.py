from seaks.features.layer import ActiveLayer

event_to_followup_actions = {}
INTERRUPT = "interrupt"


def handle_event(event_id: str) -> None:
    for event_uid, k2a in event_to_followup_actions.items():
        if event_id in k2a.keys():
            # The action is responsible for setting
            # the new set of overrides if there are any.
            actions = event_to_followup_actions.pop(event_uid)
            actions[event_id]()
            return

    ActiveLayer.handle(event_id)


def has_interrupted(event_id: str) -> bool:
    if not event_to_followup_actions:
        return False
    if event_id in []:
        return False
    handle_event(INTERRUPT)
    return True


def followup_actions_for(event_uid: str, key_to_action) -> "Callable":
    def func():
        event_to_followup_actions[event_uid] = key_to_action

    return func
