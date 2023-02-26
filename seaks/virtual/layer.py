from seaks.hardware.board import Board
from seaks.logic.action import Action
from seaks.logic.event import Event
from seaks.logic.state import State
from seaks.utils.memory import memory_cost
from seaks.virtual.switch import Switch


class Layer:
    instances: dict[str, "Layer"] = {}

    @memory_cost("vLayer")
    def __init__(self, physical_board: Board, name, state: State) -> None:
        if name in Layer.instances.keys():
            raise KeyError(f"A layer with the name '{name}' already exists.")
        Layer.instances[name] = self
        self.state = state
        switches = Switch.instanciate(name, physical_board)
        self.switches = switches
        for switch in switches:

            def wrap_event(switch_name, value):
                def func():
                    Event.get(switch_name, value).fire()
                    return True

                return Action(func)

            state.add_trigger(
                Event.get(f"switch.{switch.switch_id}", True),
                wrap_event(switch.name, True),
            )
            state.add_trigger(
                Event.get(f"switch.{switch.switch_id}", False),
                wrap_event(switch.name, False),
            )
