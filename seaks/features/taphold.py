import re

import seaks.logic.action as action
from seaks.features.key import (
    active_patterns,
    func_mapping,
    get_actions_for,
    press_patterns,
    regex_cache,
)

# from seaks.features.key import oneshot, press, release, set_state, start_delay
from seaks.logic.event import Timer
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
    press_event_uid = key_uid
    hold_event_uid = f"{key_uid}.hold"
    interrupt_event_uid = f"{key_uid}.interrupt"
    release_event_uid = f"!{key_uid}"
    release_event_id = f"!{switch_uid}"

    # Timer to control the hold delay
    Timer(hold_event_uid, delay)

    regex_cache[press_event_uid] = re.compile(f"^{press_event_uid}$").search
    regex_cache[release_event_uid] = re.compile(f"^{release_event_id}$").search
    regex_cache[hold_event_uid] = re.compile(f"^{hold_event_uid}$").search

    interrupt_regex = lambda event_ids: (
        len(event_ids) != 0
        and True
        not in [
            event_id in event_ids.split("/")
            for event_id in [release_event_id, hold_event_uid]
        ]
    )

    regex_cache[interrupt_event_uid] = interrupt_regex
    debug = lambda x: lambda: print(x)

    clean_active_patterns = lambda: [
        active_patterns.pop(event_uid)
        for event_uid in [
            press_event_uid,
            release_event_uid,
            hold_event_uid,
            interrupt_event_uid,
        ]
        if event_uid in active_patterns.keys()
    ]

    # Tap
    on_press_tap, on_release_tap = get_actions_for(keycode_tap)
    tap_action = action.chain(
        debug("t before"),
        action.stop_timer(hold_event_uid),
        on_press_tap,
        on_release_tap,
        clean_active_patterns,
        action.claim(release_event_id),
    )

    # Hold
    on_press_hold, on_release_hold = get_actions_for(keycode_hold)
    hold_release_action = action.chain(
        debug("h r before"),
        on_release_hold,
        clean_active_patterns,
        action.claim(release_event_id),
    )
    hold_action = action.chain(
        debug("h before"),
        on_press_hold,
        lambda: active_patterns.update({release_event_uid: hold_release_action}),
        lambda: active_patterns.pop(interrupt_event_uid),
        action.claim(hold_event_uid),
        debug("h after"),
    )

    # Interrupt
    if on_interrupt == "tap":
        interrupt_release_action = action.chain(
            clean_active_patterns,
            action.claim(release_event_id),
        )
        interrupt_action = action.chain(
            debug("it before"),
            lambda: active_patterns.pop(interrupt_event_uid),
            action.stop_timer(hold_event_uid),
            on_press_tap,
            on_release_tap,
            lambda: active_patterns.update(
                {release_event_uid: interrupt_release_action}
            ),
        )
    elif on_interrupt == "hold":
        interrupt_release_action = hold_release_action
        interrupt_action = action.chain(
            debug("ih before"),
            lambda: active_patterns.pop(interrupt_event_uid),
            action.stop_timer(hold_event_uid),
            on_press_hold,
            lambda: active_patterns.update(
                {release_event_uid: interrupt_release_action}
            ),
        )
    else:
        interrupt_release_action = action.chain(
            clean_active_patterns,
            action.claim(release_event_id),
        )
        interrupt_action = action.chain(
            debug("i0 before"),
            lambda: active_patterns.pop(interrupt_event_uid),
            action.stop_timer(hold_event_uid),
            lambda: active_patterns.update(
                {release_event_uid: interrupt_release_action}
            ),
        )

    # Activate switch
    press_action = action.chain(
        lambda: active_patterns.update({release_event_uid: tap_action}),
        lambda: active_patterns.update({hold_event_uid: hold_action}),
        lambda: active_patterns.update({interrupt_event_uid: interrupt_action}),
        action.start_timer(hold_event_uid, True),
        action.claim(press_event_uid),
    )

    press_patterns[1][press_event_uid] = press_action


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
