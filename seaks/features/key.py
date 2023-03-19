from collections import namedtuple

from seaks.logic.action import Action
from seaks.logic.event import Event, Timer
from seaks.logic.state import StateMachine
from seaks.utils.memory import check_memory

# Aliases to improve code readability
chain = Action.chain
oneshot = Action.oneshot
press = Action.press
release = Action.release
set_state = Action.state

Key = namedtuple("Key", ["name", "key", "status"])


def start_delay(timer_name: str) -> Action:
    def func():
        Timer.start(timer_name)
        return True

    return Action(func)


instances: dict[str, dict[str, Key]] = {}


@check_memory("Key")
def create(input: tuple[str, str]) -> Key:
    layer_name, switch_id = input
    key_name = str.upper(key_name)
    full_key_name = f"{layer_name}.switch.{switch_id}"

    print(f"\nKey: '{full_key_name}'")

    enter_layer = Event.get(f"{layer_name}", True)
    exit_layer = Event.get(f"{layer_name}", False)
    press_key = Event.get(f"{layer_name}.switch.{switch_id}", True)
    release_key = Event.get(f"switch.{switch_id}", False)

    # TODO: Share the machine at the board level
    status = StateMachine(
        f"{layer_name}.status.{key_name}",
        ["asleep", "listening", "active", "zombie"],
    )
    key = StateMachine(f"{full_key_name}", ["asleep", "released", "pressed"])

    # Setup the status state machine
    status["asleep"].add_trigger(enter_layer, set_state(status, "listening"))
    status["listening"].add_trigger(exit_layer, set_state(status, "asleep"))
    status["listening"].add_trigger(press_key, set_state(status, "active"))
    status["active"].add_trigger(release_key, set_state(status, "listening"))
    status["active"].add_trigger(exit_layer, set_state(status, "zombie"))
    status["zombie"].add_trigger(
        release_key,
        chain(set_state(status, "asleep"), set_state(key, "asleep"), release(key_name)),
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
    new_key = Key(full_key_name, key, status)
    instances[layer_name] = instances.get(layer_name, {})
    instances[layer_name][switch_id] = new_key
    return new_key


def get(input: tuple[str, str]) -> Key:
    layer_name, switch_id = input
    try:
        return instances[layer_name][switch_id]
    except KeyError as ex:
        print(f"Keys: {instances.keys()}")
        print(f"Key not found: {input}")
        for l, sw in instances.items():
            print([(l, s) for s in sw])

        return create((layer_name, switch_id))
