from collections import namedtuple

from seaks.hardware.board import Board as HardwareBoard
from seaks.logic.state import StateMachine
from seaks.utils.memory import memory_cost

Switch = namedtuple("Switch", ["name", "switch_id", "status", "key"])


def create(name: str, switch_id: str) -> Switch:
    status = StateMachine(f"{name}.status", ["asleep", "listening", "active", "zombie"])
    key = StateMachine(f"{name}.key", ["asleep", "released", "pressed"])
    return Switch(name, switch_id, status, key)


@memory_cost("vSwitchMatrix")
def instanciate_matrix(name: str, board: HardwareBoard) -> list["Switch"]:
    switches: list["Switch"] = []
    for switch in board.switches:
        switches.append(create(f"{name}.{switch.name}", switch.id))
    return switches
