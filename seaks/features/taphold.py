from seaks.event import Timer, Trigger
from seaks.features.key import (
    Key,
    chain,
    oneshot,
    press,
    release,
    set_state,
    start_delay,
)


class TapHold:
    def __init__(
        self, input: list[str], key_names: list[str], delay: float = 0.3
    ) -> None:
        layer, switch = input
        key_names = [str.upper(name) for name in key_names]

        # Create a standard key, and get the key StateMachine
        key = Key.get((layer, switch), key_names[0]).key

        # Timer to control the hold delay
        timer_name = f"{key.name}.tap_delay"
        Timer(Trigger(timer_name, True), delay, timer_name, False)

        # Aliases
        delay_timeout = Trigger(timer_name, True)
        press_key = Trigger(f"switch.{switch}", True)
        release_key = Trigger(f"switch.{switch}", False)
        reset_delay = start_delay(timer_name)

        # Modify the StateMachine to enable TapHold
        for key_name in reversed(key_names[:-1]):
            key.add_state(f"hold_{key_name}")

        current_state = "released"
        new_state = f"hold_{key_name}"
        key[current_state].add_trigger(
            press_key, chain(set_state(key, new_state), reset_delay)
        )
        current_state, current_key_name = new_state, key_names[0]
        for key_name in key_names[1:-1]:
            print("Setup", key_name)
            new_state = f"hold_{key_name}"
            key[current_state].add_trigger(
                release_key,
                chain(set_state(key, "released"), oneshot(current_key_name)),
            )
            key[current_state].add_trigger(
                delay_timeout, chain(set_state(key, new_state), reset_delay)
            )
            current_state, current_key_name = new_state, key_name
        new_state = "pressed"
        key[current_state].add_trigger(
            release_key, chain(set_state(key, "released"), oneshot(current_key_name))
        )
        key[current_state].add_trigger(
            delay_timeout, chain(set_state(key, "pressed"), press(key_names[-1]))
        )
        key["pressed"].add_trigger(
            release_key, chain(set_state(key, "released"), release(key_names[-1]))
        )
