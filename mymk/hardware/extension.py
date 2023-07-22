from mymk.hardware.baseboard import BaseBoard
from mymk.utils.logger import logger
from mymk.utils.memory import no_gc


class Keyboard(BaseBoard):
    def __init__(self, definition: dict) -> None:
        super().__init__(definition, True)
        self.channel.send(self.keymatrix.key_count, 8)
        self.message_length = self.keymatrix.key_count.bit_length() + 2
        self.color = None

    def get_key_event(self) -> int:
        data = 0 << self.message_length - 1
        event = self.keymatrix.events.get()
        if not event:
            return data
        data |= 1

        if event.pressed:
            data |= 2
        data |= event.key_number << 2

        return data

    def send_event(self) -> None:
        data = self.get_key_event()
        self.channel.send(data, self.message_length)

    def get_controller_data(self) -> None:
        # Receive message from Controller about a possible led color change
        color = []
        for _ in range(3):
            color.append(self.channel.receive(8))
        if color != self.color:
            self.pixels.fill(color)
            self.color = color
            # logger.info("Set color: %s", color)

    @no_gc
    def tick(self) -> None:
        if not hasattr(self, "loop"):
            setattr(self, "loop", 0)
        self.loop += 1
        logger.info("Loop %s", self.loop)
        self.send_event()
        self.get_controller_data()

    def go(self, _: bool = False) -> None:
        while True:
            self.tick()
