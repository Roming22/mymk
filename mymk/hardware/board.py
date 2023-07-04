from time import sleep

from mymk.hardware.baseboard import BaseBoard
from mymk.multiverse.timeline_manager import TimelineManager
from mymk.utils.memory import memory_cost

from mymk.utils.logger import logger
# from mymk.utils.memory import get_usage

class Board(BaseBoard):
    @memory_cost("Board")
    def __init__(self, definition: dict) -> None:
        super().__init__(definition)
        self.switch_offset = 0
        if self.channel:
            self.channel.sync()
            extension_switch_count = self.channel.receive(8)
            logger.info("Extension has %s switches.", extension_switch_count)
            self.message_length = extension_switch_count.bit_length() + 2
        if self.is_right:
            self.switch_offset = extension_switch_count

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

    def get_event_extension(self) -> str:
        event_id = ""
        data = self.channel.receive(self.message_length)
        has_event = data & 1
        if has_event:
            data >>= 1
            is_pressed = data & 1
            data >>= 1
            event_id = f"board.{self.name}.switch.{data}"
            if not is_pressed:
                event_id = f"!{event_id}"
        return event_id

    def send_extension_data(self) -> None:
        for color in (255, 0, 255):
            self.channel.send(color, 8)

    def tick(self) -> None:
        # self.loop += 1
        # logger.info("Loop %s: %s", self.loop, get_usage(True))
        if event_id := self.get_event_controller():
            TimelineManager.process_event(event_id)
        if self.channel:
            self.channel.sync()
            if event_id := self.get_event_extension():
                TimelineManager.process_event(event_id)
            self.send_extension_data()
