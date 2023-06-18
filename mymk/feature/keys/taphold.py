from mymk.feature.keys.key import Key
from mymk.hardware.keys import press, release
from mymk.logic.timer import Timer
from mymk.utils.memory import memory_cost

delay = 0.3


# @memory_cost("TapHold")
def tap_hold(interrupt_mode: str, universe, switch_uid: str, data) -> None:
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

    timer_name = f"timer.{switch_uid}.taphold"

    # print(
    #     f"TapHold ({key_delay}s): {keycode_tap} | {keycode_hold} ({keycode_interrupt})"
    # )

    # Tap
    timeline = universe.split(f"{switch_uid} press/release tap {keycode_tap}")
    timer_name_tap = f"{timer_name}.tap.{keycode_tap}"
    timer_tap = Timer(timer_name_tap, key_delay, universe, timeline)
    events = {
        f"!{switch_uid}": [(f"!{switch_uid}", [timer_tap.stop, timeline.mark_determined], [release(keycode_tap)])],
    }
    timeline.events.update(events)
    timeline.output.append(press(keycode_tap))

    # Hold
    timeline = universe.split(f"{switch_uid} press/release hold {keycode_hold}")
    timer_name_hold = f"{timer_name}.hold.{keycode_hold}"
    Timer(timer_name_hold, key_delay, universe, timeline)
    events = {
        timer_name_hold: [
            (timer_name_hold, [timeline.mark_determined], []),
            (f"!{switch_uid}", [], [release(keycode_hold)])
        ],
    }
    timeline.events.update(events)
    timeline.output.append(press(keycode_hold))

    # Interrupt
    timeline = universe.split(f"{switch_uid} press/release interrupt {keycode_interrupt}")
    timer_name_interrupt = f"{timer_name}.interrupt.{keycode_interrupt}"
    timer_interrupt = Timer(timer_name_interrupt, key_delay, universe, timeline)
    events = {
        "interrupt": [
            ("interrupt", [timer_interrupt.stop, timeline.mark_determined], []),
            (f"!{switch_uid}", [], [release(keycode_interrupt)])
        ],
    }
    timeline.events.update(events)
    timeline.output.append(press(keycode_interrupt))


Key.loader_map["TH_HD"] = lambda *args, **kwargs: tap_hold("hold", *args, **kwargs)
Key.loader_map["TH_NO"] = lambda *args, **kwargs: tap_hold("noop", *args, **kwargs)
Key.loader_map["TH_TP"] = lambda *args, **kwargs: tap_hold("tap", *args, **kwargs)
