from random import randint

import keypad
import storage

from mymk.hardware.leds import Pixel
from mymk.utils.logger import logger


class Board:
    def __init__(self, definition: dict) -> None:
        self.name = storage.getmount("/").label
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

    def get_key_event(self):
        event = self.keymatrix.events.get()
        if not event:
            return (None, None)
        switch_uid = event.key_number
        if self.switch_offset:
            switch_uid += self.switch_offset
        return ("{switch_uid}", event.pressed)


    def tick(self) -> None:
        switch_uid, is_pressed = self.get_key_event()
        # TODO: Send event to controller
        # send((event.pressed, switch_uid))
        # TODO: Get event from controller
        # send((event.pressed, switch_uid))
        if switch_uid:
            logger.info("Switch uid, pressed: %s = %s", switch_uid, is_pressed)
            if is_pressed:
                color = (randint(0, 255), randint(0, 255), randint(0, 255))
            else:
                color = (0, 0, 0)
            self.pixels.fill(color)

    def go(self, _: bool = False):
        while True:
            self.tick()
