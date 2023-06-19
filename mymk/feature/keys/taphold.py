from mymk.hardware.keys import press, release
from mymk.logic.keys import load, loader_map
from mymk.logic.timer import Timer
from mymk.utils.memory import memory_cost

delay = 0.3


# @memory_cost("TapHold")
def load_taphold(interrupt_mode: str, universe, switch_uid: str, data) -> None:
    keycode_tap = data.pop(0)
    keycode_hold = data.pop(-1)

    if interrupt_mode == "HD":
        keycode_interrupt = keycode_hold
    elif interrupt_mode == "TP":
        keycode_interrupt = keycode_tap
    else:
        keycode_interrupt = "NO"
    if data:
        key_delay = float(data.pop(0))
    else:
        key_delay = delay

    timer_name = f"timer.{switch_uid}.TH_{interrupt_mode}({keycode_tap},{keycode_hold})"

    # print(
    #     f"TapHold ({key_delay}s): {keycode_tap} | {keycode_hold} ({keycode_interrupt})"
    # )

    # Tap
    timeline = universe.split(f"{switch_uid} press/release tap {keycode_tap}")
    timer_name_tap = f"{timer_name}.tap"
    timer_tap = Timer(timer_name_tap, key_delay, universe, timeline)
    events = {
        f"!{switch_uid}": [
            (
                f"!{switch_uid}",
                [timer_tap.stop, timeline.mark_determined],
                [press(keycode_tap), release(keycode_tap)],
            )
        ],
    }
    timeline.events.update(events)

    # Interrupt
    timeline = universe.split(
        f"{switch_uid} press/release interrupt {keycode_interrupt}"
    )
    timer_name_interrupt = f"{timer_name}.interrupt"
    timer_interrupt = Timer(timer_name_interrupt, key_delay, universe, timeline)
    events = {
        "interrupt": [
            (
                "interrupt",
                [
                    timer_interrupt.stop,
                    lambda: load(switch_uid, keycode_interrupt, universe),
                ],
                [],
            ),
        ],
    }
    timeline.events.update(events)

    # Hold
    timeline = universe.split(f"{switch_uid} press/release hold {keycode_hold}")
    timer_name_hold = f"{timer_name}.hold"
    Timer(timer_name_hold, key_delay, universe, timeline)
    events = {
        timer_name_hold: [
            (timer_name_hold, [lambda: load(switch_uid, keycode_hold, universe)], []),
        ],
    }
    timeline.events.update(events)


loader_map["TH_HD"] = lambda *args, **kwargs: load_taphold("HD", *args, **kwargs)
loader_map["TH_NO"] = lambda *args, **kwargs: load_taphold("NO", *args, **kwargs)
loader_map["TH_TP"] = lambda *args, **kwargs: load_taphold("TP", *args, **kwargs)
