from random import randint

import keypad
import storage

from mymk.hardware.leds import Pixel
from mymk.multiverse.timeline_manager import TimelineManager
from mymk.utils.memory import memory_cost


def get_drive_name() -> bool:
    return storage.getmount("/").label


class Board:
    @memory_cost("Board")
    def __init__(self, definition: dict) -> None:
        self.name = get_drive_name()
        board_definition = definition["hardware"][self.name]
        self.is_left = not self.name.endswith("R")

        # Set leds as early as possible to give some feedback on the boot sequence
        leds = board_definition.get("leds")
        if leds:
            # Barely light up the leds to show that the keyboard is booting
            color = (4, 0, 0) if self.is_left else (0, 4, 0)
            pin = leds.get("pin")
            self.pixels = Pixel.create(pin, leds["count"], color)
        else:
            self.pixels = None

        # Create matrix
        self.keymatrix = keypad.KeyMatrix(
            row_pins=board_definition["pins"]["rows"],
            column_pins=board_definition["pins"]["cols"],
        )

        # Deal with split keyboards
        if self.is_left:
            self.switch_offset = 0
        else:
            left_board_definition = [
                v for k, v in definition["hardware"].items() if k.endswith("L")
            ][0]
            switch_count_left = len(left_board_definition["pins"]["cols"]) * len(
                left_board_definition["pins"]["rows"]
            )
            self.switch_offset = switch_count_left

    def get_event_controller(self) -> str:
        event = self.keymatrix.events.get()
        if not event:
            return ""
        switch_uid = event.key_number
        if self.switch_offset:
            switch_uid += self.switch_offset
        event_id = f"board.{self.name}.switch.{switch_uid}"
        if event.released:
            event_id = f"!{event_id}"
        return event_id

    def tick(self) -> None:
        if event_id := self.get_event_controller():
            TimelineManager.process_event(event_id)
