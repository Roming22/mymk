from seaks.action import Action
from seaks.buffer import Buffer
from seaks.event import Trigger
from seaks.hardware.keys import press, release
from seaks.state import State


class Key:
    def __init__(self, switch: str, key_name: str, layer: State) -> None:
        key_name = str.upper(key_name)
        print(f"Key: '{key_name}'")
        layer.add_trigger(Trigger(f"switch.{switch}", True), Action.press(key_name))
        layer.add_trigger(Trigger(f"switch.{switch}", False), Action.release(key_name))
        for event_sequence, action in [
            (key_name, Buffer.clear_after(press(key_name))),
            (str.lower(key_name), Buffer.clear_after(release(key_name))),
        ]:
            Buffer.register_event_sequence(event_sequence, action)
