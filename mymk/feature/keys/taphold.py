from mymk.feature.keys.key import Key
from mymk.hardware.keys import press, release
from mymk.utils.memory import memory_cost

delay = 0.5


@memory_cost("TapHold")
def tap_hold(
    interrupt_mode: str,
    universe,
    switch_uid: str,
    data,
) -> list:
    keycode_tap = data.pop(0)
    keycode_hold = data.pop(-1)

    if interrupt_mode == "hold":
        keycode_interrupt = keycode_hold
    elif interrupt_mode == "tap":
        keycode_interrupt = keycode_tap
    else:
        keycode_interrupt = "NO"

    try:
        key_delay = data.pop(0)
    except IndexError:
        key_delay = delay

    print(
        f"TapHold ({key_delay}s): {keycode_tap} | {keycode_hold} ({keycode_interrupt})"
    )

    timelines_events = [
        # Tap
        {
            switch_uid: [
                (switch_uid, None, press(keycode_tap)),
                (f"!{switch_uid}", universe.mark_determined, release(keycode_tap)),
            ],
        },
        # Hold
        {
            switch_uid: [
                (switch_uid, None, press(keycode_hold)),
                (f"timer.{switch_uid}.taphold", universe.mark_determined, None),
                (f"!{switch_uid}", None, release(keycode_hold)),
            ]
        },
        # Interrupt
        {
            switch_uid: [
                (switch_uid, None, press(keycode_interrupt)),
                (f"interrupt", universe.mark_determined, None),
                (f"!{switch_uid}", None, release(keycode_interrupt)),
            ]
        },
    ]

    return timelines_events


Key.loader_map["TH_HD"] = lambda *args, **kwargs: tap_hold("hold", *args, **kwargs)
Key.loader_map["TH_NO"] = lambda *args, **kwargs: tap_hold("noop", *args, **kwargs)
Key.loader_map["TH_TP"] = lambda *args, **kwargs: tap_hold("tap", *args, **kwargs)
