from collections import namedtuple

from seaks.logic.action import Action
from seaks.hardware.board import Board as HardwareBoard
from seaks.logic.event import Event, Timer
from seaks.logic.state import StateMachine
from seaks.utils.memory import check_memory

# Aliases to improve code readability
chain = Action.chain
oneshot = Action.oneshot
press = Action.press
release = Action.release
set_state = Action.state

Switch = namedtuple("Switch", ["name", "switch_id", "status", "key"])


def create(layer_name: str, switch_id: str) -> Switch:
    name=f"{layer_name}.switch.{switch_id}"
    status = StateMachine(f"{name}.status", ["asleep", "listening", "active", "zombie"])
    key = StateMachine(f"{name}.key", ["asleep", "released", "pressed"])

    enter_layer = Event.get(f"{layer_name}", True)
    exit_layer = Event.get(f"{layer_name}", False)
    press_key = Event.get(name, True)
    release_key = Event.get(f"switch.{switch_id}", False)

    # Setup the status state machine
    status["asleep"].add_trigger(enter_layer, set_state(status, "listening"))
    status["listening"].add_trigger(exit_layer, set_state(status, "asleep"))
    status["listening"].add_trigger(press_key, set_state(status, "active"))
    status["active"].add_trigger(release_key, set_state(status, "listening"))
    status["active"].add_trigger(exit_layer, set_state(status, "zombie"))
    status["zombie"].add_trigger(
        release_key,
        chain(set_state(status, "asleep"), set_state(key, "asleep"), release(name)),
    )

    # Setup the key state machine
    key["asleep"].add_trigger(enter_layer, set_state(key, "released"))
    key["released"].add_trigger(exit_layer, set_state(key, "asleep"))
    key["released"].add_trigger(
        press_key, chain(set_state(key, "pressed"), press(name))
    )
    key["pressed"].add_trigger(
        release_key, chain(set_state(key, "released"), release(name))
    )

    key = StateMachine(f"{name}.key", ["asleep", "released", "pressed"])
    return Switch(name, switch_id, status, key)


@check_memory("vSwitchMatrix")
def instanciate_matrix(layer_name: str, board: HardwareBoard) -> list["Switch"]:
    switches: list["Switch"] = []
    for switch in board.switches:
        switches.append(create(layer_name, switch.id))
    return switches
