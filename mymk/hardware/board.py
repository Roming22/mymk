import keypad

from mymk.hardware.leds import create as create_pixels
from mymk.multiverse.timeline_manager import TimelineManager
from mymk.utils.memory import memory_cost


class Board:
    _instances = []

    @memory_cost("Board")
    def __init__(self, name: str, definition: dict) -> None:
        self.name = name
        leds = definition.get("leds")
        if leds:
            # Barely light up the leds to show that the keyboard is booting
            color = (4, 0, 0)
            pin = leds.get("pin")
            self.pixels = create_pixels(pin, leds["count"], color)
        else:
            self.pixels = None
        self.keymatrix = keypad.KeyMatrix(
            row_pins=definition["pins"]["rows"],
            column_pins=definition["pins"]["cols"],
        )
        Board._instances.append(self)

    def get_event(self) -> str:
        event = self.keymatrix.events.get()
        if not event:
            return ""
        event_id = f"board.{self.name}.switch.{event.key_number}"
        if event.released:
            event_id = f"!{event_id}"
        return event_id

    @classmethod
    def tick(cls) -> None:
        for board in cls._instances:
            if event_id := board.get_event():
                TimelineManager.process_event(event_id)
