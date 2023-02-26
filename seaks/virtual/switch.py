from seaks.hardware.board import Board as PhysicalBoard
from seaks.hardware.switch import Switch as PhysicalSwitch
from seaks.logic.state import StateMachine


class Switch:
    def __init__(self, name: str, switch_id: str) -> None:
        self.name = name
        self.switch_id = switch_id
        self.status = StateMachine(
            f"{name}.status", ["asleep", "listening", "active", "zombie"]
        )
        self.key = StateMachine(f"{name}.key", ["asleep", "released", "pressed"])

    @classmethod
    def instanciate(cls, name: str, board: PhysicalBoard) -> list["Switch"]:
        switches: list["Switch"] = []
        for switch in board.switches:
            switches.append(cls(f"{name}.{switch.name}", switch.id))
        return switches
