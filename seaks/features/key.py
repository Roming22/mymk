from seaks.action import Action
from seaks.event import Timer, Trigger
from seaks.state import State, StateMachine

# Aliases to improve code readability
chain = Action.chain
oneshot = Action.oneshot
press = Action.press
release = Action.release
set_state = Action.state


def start_delay(timer_name: str) -> Action:
    def func():
        Timer.start(timer_name)
        return True

    return Action(func)


class Key:
    definitions = {}

    def __init__(self, input: tuple[str], key_name: str) -> None:
        layer_name, switch_id = input
        Key.definitions[layer_name] = Key.definitions.get(layer_name, {})
        Key.definitions[layer_name][switch_id] = self
        key_name = str.upper(key_name)
        full_key_name = f"layer.{layer_name}.key{switch_id:03d}.{key_name}"
        self.name = full_key_name

        print(f"\nKey: '{full_key_name}'")

        enter_layer = Trigger(f"layer.{layer_name}", True)
        exit_layer = Trigger(f"layer.{layer_name}", False)
        press_key = Trigger(f"switch.{switch_id}", True)
        release_key = Trigger(f"switch.{switch_id}", False)

        status = StateMachine(
            f"layer.{layer_name}.status.{key_name}",
            ["asleep", "listening", "active", "zombie"],
        )
        key = StateMachine(f"{full_key_name}", ["asleep", "released", "pressed"])

        # Keep a reference to the state machine so it can
        # be modified later on by Combos and TapHold
        self.key = key

        # Setup the status state machine
        status["asleep"].add_trigger(enter_layer, set_state(status, "listening"))
        status["listening"].add_trigger(exit_layer, set_state(status, "asleep"))
        status["listening"].add_trigger(press_key, set_state(status, "active"))
        status["active"].add_trigger(release_key, set_state(status, "listening"))
        status["active"].add_trigger(exit_layer, set_state(status, "zombie"))
        status["zombie"].add_trigger(
            release_key,
            chain(
                set_state(status, "asleep"), set_state(key, "asleep"), release(key_name)
            ),
        )

        # Setup the key state machine
        key["asleep"].add_trigger(enter_layer, set_state(key, "released"))
        key["released"].add_trigger(exit_layer, set_state(key, "asleep"))
        key["released"].add_trigger(
            press_key, chain(set_state(key, "pressed"), press(key_name))
        )
        key["pressed"].add_trigger(
            release_key, chain(set_state(key, "released"), release(key_name))
        )

    @classmethod
    def get(cls, input: tuple[str], key_name: str = "") -> "Key":
        layer_name, switch_id = input
        try:
            return cls.definitions[layer_name][switch_id]
        except KeyError as ex:
            if key_name:
                return cls((layer_name, switch_id), key_name)
            raise ex


#
