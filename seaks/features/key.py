from seaks.hardware.board import Board
from seaks.logic.action import Action
from seaks.logic.event import Timer, Trigger
from seaks.logic.state import StateMachine
from seaks.utils.memory import memory_cost

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

    @memory_cost("Key")
    def __init__(self, input: tuple[str, str], key_name: str) -> None:
        layer_name, switch_id = input
        Key.definitions[layer_name] = Key.definitions.get(layer_name, {})
        Key.definitions[layer_name][switch_id] = self
        key_name = str.upper(key_name)
        full_key_name = f"{layer_name}.key.{switch_id}.{key_name}"
        self.name = full_key_name

        print(f"\nKey: '{full_key_name}'")

        enter_layer = Trigger(f"{layer_name}", True)
        exit_layer = Trigger(f"{layer_name}", False)
        press_key = Trigger(f"{layer_name}.switch.{switch_id}", True)
        release_key = Trigger(f"switch.{switch_id}", False)

        status = StateMachine(
            f"{layer_name}.status.{key_name}",
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
    def get(cls, input: tuple[str, str], key_name: str = "") -> "Key":
        layer_name, switch_id = input
        try:
            return cls.definitions[layer_name][switch_id]
        except KeyError as ex:
            if key_name:
                return cls((layer_name, switch_id), key_name)
            raise ex
