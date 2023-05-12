import seaks.logic.action as action
import seaks.logic.event_handler as EventHandler
from seaks.features.key import action_func, get_actions_for
from seaks.utils.memory import memory_cost

delay = [0.5]


@memory_cost("TapHold")
def _tap_hold(
    key_uid: str,
    keycode_tap: str,
    keycode_hold: str,
    interrupt_mode: str,
    delay: float = delay,
) -> tuple:
    hold_event_id = f"{key_uid}.hold"

    if not key_uid in EventHandler.event_to_followup_actions.keys():
        EventHandler.event_to_followup_actions[key_uid] = {}

    # Timer to control the hold delay
    start_timer = action.start_timer(hold_event_id, delay)
    stop_timer = action.stop_timer(hold_event_id)

    on_press = start_timer

    # Tap
    on_press_tap, on_release_tap, _ = get_actions_for(key_uid, keycode_tap)
    on_release = action.chain(
        stop_timer,
        on_press_tap,
        on_release_tap,
    )

    # Hold
    hold_action = lambda: EventHandler.handle_keycode(key_uid, keycode_hold)
    EventHandler.event_to_followup_actions[key_uid][hold_event_id] = hold_action

    # Interrupt
    if interrupt_mode == "tap":
        on_interrupt = on_release
    elif interrupt_mode == "hold":
        on_interrupt = action.chain(
            stop_timer,
            hold_action,
        )
    else:
        on_interrupt = action.chain(
            stop_timer,
        )
    return (on_press, on_release, on_interrupt)


def _get_delay(user_delay: str) -> float:
    if user_delay:
        _delay = float(user_delay)
    else:
        _delay = delay[0]
    return _delay


def hold_tap(
    switch_uid: str,
    keycode_tap: str,
    keycode_hold: str,
    user_delay: str = "",
) -> tuple:
    print("Creating HoldTap:", switch_uid, keycode_tap, delay, keycode_hold)
    return _tap_hold(
        switch_uid, keycode_tap, keycode_hold, "hold", _get_delay(user_delay)
    )


def interrupt_noop(
    switch_uid: str,
    keycode_tap: str,
    keycode_hold: str,
    user_delay: str = "",
) -> tuple:
    print(
        "Creating interruptible TapHold:", switch_uid, keycode_tap, delay, keycode_hold
    )
    return _tap_hold(
        switch_uid, keycode_tap, keycode_hold, "noop", _get_delay(user_delay)
    )


def tap_hold(
    switch_uid: str,
    keycode_tap: str,
    keycode_hold: str,
    user_delay: str = "",
) -> tuple:
    print("Creating TapHold:", switch_uid, keycode_tap, delay, keycode_hold)
    return _tap_hold(
        switch_uid, keycode_tap, keycode_hold, "tap", _get_delay(user_delay)
    )


action_func["TH_NO"] = interrupt_noop
action_func["TH_HD"] = hold_tap
action_func["TH_TP"] = tap_hold
