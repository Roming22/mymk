from mymk.feature.keys.key import Key
from mymk.hardware.keys import press, release
from mymk.logic.action import chain
from mymk.logic.timer import Timer
from mymk.utils.memory import memory_cost

delay = 0.3


# @memory_cost("TapHold")
def tap_hold(interrupt_mode: str, universe, switch_uid: str, data) -> list:
    keycode_tap = data.pop(0)
    keycode_hold = data.pop(-1)

    if interrupt_mode == "hold":
        keycode_interrupt = keycode_hold
    elif interrupt_mode == "tap":
        keycode_interrupt = keycode_tap
    else:
        keycode_interrupt = "NO"

    try:
        key_delay = float(data.pop(0))
    except IndexError:
        key_delay = delay

    # print(
    #     f"TapHold ({key_delay}s): {keycode_tap} | {keycode_hold} ({keycode_interrupt})"
    # )

    timer_name = f"timer.{switch_uid}.taphold"
    timer_tap = Timer(timer_name, key_delay, universe)
    timer_hold = Timer(timer_name, key_delay, universe)
    timer_interrupt = Timer(timer_name, key_delay, universe)

    timelines_events = [
        # Tap
        {
            "what": f"{switch_uid} tap",
            switch_uid: [
                (switch_uid, timer_tap.start, press(keycode_tap)),
                (
                    f"!{switch_uid}",
                    chain(
                        timer_tap.stop,
                        timer_hold.stop,
                        timer_interrupt.stop,
                        universe.mark_determined,
                    ),
                    release(keycode_tap),
                ),
            ],
        },
        # Hold
        {
            "what": f"{switch_uid} hold",
            switch_uid: [
                (switch_uid, timer_hold.start, press(keycode_hold)),
                (timer_name, universe.mark_determined, None),
                (f"!{switch_uid}", None, release(keycode_hold)),
            ],
        },
        # Interrupt
        {
            "what": f"{switch_uid} interrupt",
            switch_uid: [
                (switch_uid, timer_interrupt.start, press(keycode_interrupt)),
                (
                    f"interrupt",
                    chain(timer_tap.stop, timer_hold.stop, universe.mark_determined),
                    None,
                ),
                (f"!{switch_uid}", None, release(keycode_interrupt)),
            ],
        },
    ]

    return timelines_events


Key.loader_map["TH_HD"] = lambda *args, **kwargs: tap_hold("hold", *args, **kwargs)
Key.loader_map["TH_NO"] = lambda *args, **kwargs: tap_hold("noop", *args, **kwargs)
Key.loader_map["TH_TP"] = lambda *args, **kwargs: tap_hold("tap", *args, **kwargs)
