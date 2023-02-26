from collections import namedtuple

from seaks.hardware.board import Board
from seaks.logic.action import Action
from seaks.logic.event import Event
from seaks.logic.state import State
from seaks.utils.memory import memory_cost
from seaks.virtual.switch import instanciate_matrix as instanciate_switch_matrix

Layer = namedtuple("Layer", ["name", "state", "switches"])

instances: dict[str, Layer] = {}


@memory_cost("vLayer")
def create(hardware_board: Board, name, state: State) -> Layer:
    if name in instances.keys():
        raise KeyError(f"A layer with the name '{name}' already exists.")
    switches = instanciate_switch_matrix(name, hardware_board)

    for switch in switches:

        def wrap_event(switch_name, value):
            event = Event.get(switch_name, value)

            def func():
                event.fire()
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
    layer = Layer(name, state, switches)
    instances[name] = layer
    return layer
