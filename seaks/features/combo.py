from seaks.features.key import chain
from seaks.features.key import get as get_key
from seaks.features.key import oneshot, press, release, set_state, start_delay
from seaks.logic.action import Action
from seaks.logic.event import Event, Timer
from seaks.utils.memory import check_memory
from seaks.utils.toolbox import permutations


# Creates function to transform/revert any key to/from a TapHold
def make_comb_func(
    combo_name: str, keys: list[tuple[str, str]], key_name: str, timer_name
):
    key = get_key(keys[0]).key
    layer, switch = keys[0]

    def func():
        # Aliases
        delay_timeout = Event.get(timer_name, True)
        press_key = Event.get(f"{layer}.switch.{switch}", True)
        release_key = Event.get(f"switch.{switch}", False)
        reset_delay = start_delay(timer_name)

        print(f"Keys: {key['released'].triggers.keys()}")
        default_released_action = key["released"].triggers[press_key]
        if len(keys) > 1:
            key.add_state(combo_name)

            # Enable delay between key press and the next state
            key["released"].add_trigger(
                press_key, chain(set_state(key, combo_name), reset_delay)
            )
            key[combo_name].add_trigger(delay_timeout, default_released_action)

            # Make the next key aware of the combo
            make_comb_func(combo_name, keys[1:], key_name, timer_name)()

            # Disable combo if key is released
            def remove_combo():
                key["released"].add_trigger(press_key, default_released_action)
                key.states.pop(combo_name)

            key[combo_name].add_trigger(
                release_key,
                chain(set_state(key, "released"), Action(remove_combo)),
            )
        else:
            # Sequence completes on next key press
            key["released"].add_trigger(
                press_key,
                chain(
                    set_state(key, "pressed"),
                    chain(set_state(key, "pressed"), press(key_name)),
                ),
            )

            default_pressed_action = key["pressed"].triggers[release_key]

            # Disable combo if key is released
            def remove_combo():
                key["released"].add_trigger(press_key, default_released_action)
                key["pressed"].add_trigger(release_key, default_pressed_action)

            key["pressed"].add_trigger(
                release_key,
                chain(
                    set_state(key, "released"),
                    chain(release(key_name), Action(remove_combo)),
                ),
            )

    return func


class Sequence:
    @check_memory("Sequence")
    def __init__(
        self, keys: list[tuple[str, str]], key_name: str, delay: float
    ) -> None:
        key_name = str.upper(key_name)
        print("Setup", key_name)

        combo_name = ".".join([f"{layer}.{switch}" for layer, switch in keys])
        print(f"Sequence: {combo_name}")

        # Timer to control the hold delay
        timer_name = f"{combo_name}.combo_delay"
        Timer(Event.get(timer_name, True), delay, timer_name)

        make_comb_func(combo_name, keys, key_name, timer_name)()


class Chord:
    @check_memory("Chord")
    def __init__(self, keys: list[str], key_name: str) -> None:
        keys = [str.upper(k) for k in keys]
        key_name = str.upper(key_name)
        for event_sequence in permutations(keys):
            Sequence(event_sequence, key_name)
