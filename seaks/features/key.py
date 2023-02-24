from seaks.action import Action
from seaks.event import Trigger
from seaks.state import State


class Key:
    def __init__(self, switch: str, key_name: str, layer: State) -> None:
        layer.add_trigger(Trigger(f"switch.{switch}", True), Action.press(key_name))
        layer.add_trigger(Trigger(f"switch.{switch}", False), Action.release(key_name))
