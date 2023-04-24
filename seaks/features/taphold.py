import seaks.logic.action as action
import seaks.logic.event_handler as EventHandler
from seaks.features.key import func_mapping, get_actions_for
from seaks.logic.timer import Timer
from seaks.utils.memory import memory_cost

delay = [0.5]


@memory_cost("TapHold")
def _tap_hold(
    key_uid: str,
    keycode_tap: str,
    keycode_hold: str,
    on_interrupt: str,
    delay: float = delay,
) -> None:
    switch_uid = ".".join(key_uid.split(".")[-2:])
    press_event_id = key_uid
    release_event_id = f"!{switch_uid}"
    hold_event_id = f"{key_uid}.hold"

    # Timer to control the hold delay
    Timer(hold_event_id, delay)
    start_timer = action.start_timer(hold_event_id, True)
    stop_timer = action.stop_timer(hold_event_id)

    # Tap
    on_press_tap, on_release_tap = get_actions_for(keycode_tap)
    tap_action = action.chain(
        stop_timer,
        on_press_tap,
        on_release_tap,
    )

    # Hold
    on_press_hold, on_release_hold = get_actions_for(keycode_hold)
    hold_action = action.chain(
        on_press_hold,
        EventHandler.followup_actions_for(key_uid, {release_event_id: on_release_hold}),
    )

    # Interrupt
    if on_interrupt == "tap":
        interrupt_action = action.chain(
            stop_timer,
            on_press_tap,
            EventHandler.followup_actions_for(
                key_uid, {release_event_id: on_release_tap}
            ),
        )
    elif on_interrupt == "hold":
        interrupt_action = action.chain(
            stop_timer,
            on_press_hold,
            EventHandler.followup_actions_for(
                key_uid, {release_event_id: on_release_hold}
            ),
        )
    else:
        interrupt_action = action.chain(
            stop_timer,
            EventHandler.followup_actions_for(
                key_uid,
                {release_event_id: action.noop},
            ),
        )

    # Activate switch
    EventHandler.key_to_action[press_event_id] = action.chain(
        EventHandler.followup_actions_for(
            key_uid,
            {
                release_event_id: tap_action,
                hold_event_id: hold_action,
                EventHandler.INTERRUPT: interrupt_action,
            },
        ),
        start_timer,
    )


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
) -> None:
    print("Creating HoldTap:", switch_uid, keycode_tap, delay, keycode_hold)
    _tap_hold(switch_uid, keycode_tap, keycode_hold, "hold", _get_delay(user_delay))


def interrupt_noop(
    switch_uid: str,
    keycode_tap: str,
    keycode_hold: str,
    user_delay: str = "",
) -> None:
    print(
        "Creating interruptible TapHold:", switch_uid, keycode_tap, delay, keycode_hold
    )
    _tap_hold(switch_uid, keycode_tap, keycode_hold, "noop", _get_delay(user_delay))


def tap_hold(
    switch_uid: str,
    keycode_tap: str,
    keycode_hold: str,
    user_delay: str = "",
) -> None:
    print("Creating TapHold:", switch_uid, keycode_tap, delay, keycode_hold)
    _tap_hold(switch_uid, keycode_tap, keycode_hold, "tap", _get_delay(user_delay))


func_mapping["TH_NO"] = interrupt_noop
func_mapping["TH_HD"] = hold_tap
func_mapping["TH_TP"] = tap_hold
