"""Protocol to connect 2 devices through a single wire.

The connection is half-duplex. The receiving device is expected to already
be listening when another device is sending a message.

A frame is divided in 3 equal ticks.
By default the bus is HIGH.
On the first tick the bus is set to LOW. This is interreted by the receiver
as the signal that a new frame is starting.
On the second tick the bus is set to the value of the bit that is transmitted
(LOW for 0, HIGH for 1).
On the third tick the bus is reset to HIGH.

    _     _      _   ___
0:  |___|    1:  |_|
    1 2 3        1 2 3

The first and last tick allow the receiver to stay synchronized with the sender.

Each message contains a start and end frame.
"""

import digitalio
from microcontroller import delay_us

# from mymk.utils.logger import logger


class BitBangProtocol:
    def __init__(self, pin, frequency: int, is_extension: bool) -> None:
        self.gpio = digitalio.DigitalInOut(pin)
        self.gpio.switch_to_output(True)
        self.tick = 10**6 // (frequency * 3)
        self.is_extension = is_extension

    def send(self, value: int = 0, length: int = 0) -> None:
        """Send data

        Can be called with no parameters as a way to synchronize the boards."""
        bits = [(value >> i) & 1 for i in range(length)]
        # logger.info("Sending %s as %s...", value, bits)

        # Add start/end frames
        bits.insert(0, False)
        bits.append(True)

        # Send frames
        delay_us(self.tick * 64)
        for bit in bits:
            # Tick 1
            self.gpio.value = False
            delay_us(self.tick)
            # Tick 2
            self.gpio.value = bit
            delay_us(self.tick)
            # Tick 3
            self.gpio.value = True
            delay_us(self.tick)
        # logger.info("Data sent")

    def receive(self, length: int = 0) -> int:
        """Receive data

        Can be called with no parameters as a way to synchronize the boards."""
        # logger.info("Receiving %s bits", length)
        self.gpio.switch_to_input(digitalio.Pull.UP)
        delay_us(self.tick * 8)
        bits = 0 << (length + 1)

        # Receive frames
        tick = int(self.tick * 1.25)
        for index in range(length + 2):
            # Receive frame
            while self.gpio.value != False:
                pass
            delay_us(tick)
            bits |= self.gpio.value << index
            while self.gpio.value != True:
                pass

        self.gpio.switch_to_output(True)

        # Return value
        if length == 0:
            bits = 0
        else:
            bits &= ~(1 << index)
            bits >>= 1
        # logger.info("Received: %s", bits)
        return bits

    def sync(self) -> None:
        """Sync two boards

        The extension board will wait for a message from the controller board.
        The controller board sends a message to the extension board and expects a reply.

        The extension board must be already listening when the controller sends the
        message, so the controller is throttled.
        """
        # logger.info("Syncing...")
        if self.is_extension:
            self.receive(8)
            self.send(0, 8)
        else:
            delay_us(200)
            self.send(255, 8)
            self.receive(8)
