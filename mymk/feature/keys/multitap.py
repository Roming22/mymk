from mymk.logic.keys import load, loader_map
from mymk.logic.timer import Timer

# from mymk.utils.memory import memory_cost

delay = 0.2


# @memory_cost("MultiTap")
def load_multitap(universe, switch_uid: str, data: list[str]) -> None:
    key_delay = delay
    keycode_tap = data.pop(0)

    print(f"MultiTap ({key_delay}s): {data}")

    # Tap
    load(switch_uid, keycode_tap, universe)

    # MultiTap
    if data:
        keycodes_multitap = f"MT({','.join(data)})"
        timer_name = f"timer.{keycodes_multitap}.multitap"
        timeline = universe.split(f"{switch_uid}.multitap.{keycodes_multitap}")
        timer_tap = Timer(timer_name, key_delay, universe, timeline)
        events = {
            "interrupt": [("interrupt", [timeline.prune], [])],
            f"!{switch_uid}": [
                (
                    f"!{switch_uid}",
                    [lambda: timeline.events.pop("interrupt")],
                    [],
                ),
                (
                    f"{switch_uid}",
                    [
                        timer_tap.stop,
                        timeline.mark_determined,
                        lambda: load(switch_uid, keycodes_multitap, universe),
                    ],
                    [],
                ),
            ],
        }
        timeline.events.update(events)


loader_map["MT"] = load_multitap
