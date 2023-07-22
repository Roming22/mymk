from random import randint

import keypad
import storage

from mymk.hardware.bitbang import BitBangProtocol
from mymk.hardware.leds import Pixel
from mymk.utils.logger import logger


class BaseBoard:
    def __init__(self, definition: dict, is_extension: bool = False) -> None:
        self.name = storage.getmount("/").label
        self.is_split = len(definition["hardware"]) > 1
        self.is_right = self.is_split and self.name.endswith("R")
        logger.info("Board is split/right: %s/%s", self.is_split, self.is_right)

        board_definition = definition["hardware"][self.name]

        # Set leds as early as possible to give some feedback on the boot sequence
        leds = board_definition.get("leds")
        if leds:
            # Barely light up the leds to show that the keyboard is booting
            if self.is_right:
                color = (0, 4, 0)
            else:
                color = (4, 0, 0)
            pin = leds["pin"]
            self.pixels = Pixel.create(pin, leds["count"], color)
        else:
            self.pixels = None
        self.pixels_color = None

        # Create matrix
        self.keymatrix = keypad.KeyMatrix(
            row_pins=board_definition["matrix"]["rows"],
            column_pins=board_definition["matrix"]["cols"],
        )

        # Open communication channel
        if board_definition.get("data"):
            self.channel = BitBangProtocol(
                board_definition["data"]["pin"], 2000, is_extension
            )
        else:
            self.channel = None

    def set_pixels(self, color: tuple[int, int, int]) -> None:
        if self.pixels_color == color:
            return
        self.pixels_color = color
        self.pixels.fill(color)
