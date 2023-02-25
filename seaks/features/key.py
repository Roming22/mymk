from seaks.action import Action
from seaks.buffer import Buffer
from seaks.event import Timer, Trigger
from seaks.hardware.keys import press, release
from seaks.state import State, StateMachine

# Aliases to improve code readability
chain = Action.chain
press = Action.press
release = Action.release
set_state = Action.state


class Key:
    def __init__(self, switch: str, key_name: str, layer: State) -> None:
        key_name = str.upper(key_name)
        full_key_name = f"layer.{layer.name}.key.{key_name}"

        print(f"Key: '{full_key_name}'")

        enter_layer = Trigger(f"layer.{layer.name}", True)
        exit_layer = Trigger(f"layer.{layer.name}", False)
        press_key = Trigger(f"switch.{switch}", True)
        release_key = Trigger(f"switch.{switch}", False)

        status = StateMachine(
            f"layer.{layer.name}.status.{key_name}",
            ["asleep", "listening", "active", "zombie"],
        )
        key = StateMachine(f"{full_key_name}", ["asleep", "released", "pressed"])

        # Setup the status state machine
        status["asleep"].add_trigger(
            enter_layer,
            chain(set_state(status, "listening"), set_state(key, "released")),
        )
        status["listening"].add_trigger(
            exit_layer, chain(set_state(status, "asleep"), set_state(key, "asleep"))
        ),
        status["listening"].add_trigger(press_key, set_state(status, "active"))
        status["active"].add_trigger(release_key, set_state(status, "listening"))
        status["active"].add_trigger(exit_layer, set_state(status, "zombie"))
        status["zombie"].add_trigger(
            release_key, chain(set_state(status, "asleep"), set_state(key, "asleep"))
        )

        # Setup the key state machine
        key["released"].add_trigger(
            press_key, chain(set_state(key, "pressed"), press(key_name))
        )
        key["pressed"].add_trigger(
            release_key, chain(set_state(key, "released"), release(key_name))
        )
