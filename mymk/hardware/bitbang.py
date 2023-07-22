"""Protocol to connect 2 devices through a single wire.

The connection is half-duplex. A handshake ensures both devices are
synchronized before data is transmitted.

Each bit is sent in a frame, divided in 4 equal ticks.
By default the bus is HIGH.
On the first tick the bus is set to LOW. This signals the receiver that
a new frame is starting.
On the second and third tick the bus is set to the value of the bit that is transmitted
(LOW for 0, HIGH for 1).
On the fourth tick the bus is reset to HIGH.

   _       _      _   _____
0:  |_____|    1:  |_|
    1 2 3 4        1 2 3 4

The first and last tick allow the receiver to stay synchronized with the sender.

The handshake is asymmetrical.
The receiver will send a REQ by cycling the bus, quickly check for an ACK from the sender.
It repeats the procedure until an ACK has been received.
The sender waits for the REQ, then sends an ACK by cycling the bus.
"""

# pulseio might be a better fit. The protocol would need to be adapted though.
import digitalio
from microcontroller import delay_us

from mymk.utils.logger import logger


class BitBangProtocol:
    def __init__(self, pin, frequency: int, is_extension: bool) -> None:
        self.gpio = digitalio.DigitalInOut(pin)
        self.gpio.switch_to_output(True, digitalio.DriveMode.OPEN_DRAIN)
        # Number of ticks:
        # 2 ticks for the _ping in _handshake_receive
        # 2 ticks for the _ping in _handshake_send
        # 4 ticks in send
        # 2 ticks for the _ping in send
        send_frequency = 200
        read_frequency = 8
        ticks_per_frame = 10
        self.tick_send = int(10**6 // (send_frequency * ticks_per_frame))
        self.tick_read = self.tick_send // read_frequency
        logger.info(
            "Frequency: %s    Send: %s    Read: %s",
            1 // (ticks_per_frame * self.tick_send * 10**-6),
            self.tick_send,
            self.tick_read,
        )
        self.is_extension = is_extension

    def _ping(self):
        self.gpio.switch_to_output(True, digitalio.DriveMode.OPEN_DRAIN)
        self.gpio.value = False
        delay_us(self.tick_send)
        self.gpio.value = True
        delay_us(self.tick_send)

    def _wait_for(self, value: bool):
        for _ in range(1 + self.tick_send // self.tick_read):
            if self.gpio.value == value:
                return
            delay_us(self.tick_read)
        raise RuntimeError(f"Failed to receive {value}")

    def _handshake_send(self):
        # logger.info("Waiting for the handshake as sender")
        # Wait for REQ
        self.gpio.switch_to_input(digitalio.Pull.UP)
        while self.gpio.value != False:
            delay_us(self.tick_read)
        self._wait_for(True)
        delay_us(self.tick_send)

        # Send ACK
        self._ping()
        # logger.info("Handshake complete as sender")

    def _handshake_receive(self):
        # logger.info("Initiating handshake as receiver")
        while True:
            # logger.info("Sending handshake")
            # Send REQ
            self._ping()
            # Wait for ACK
            self.gpio.switch_to_input(digitalio.Pull.UP)
            try:
                self._wait_for(False)
            except:
                continue
            try:
                self._wait_for(True)
                return
            except:
                raise RuntimeError("Failed ACK")

    def send(self, value: int = 0, length: int = 1) -> None:
        """Send data

        Can be called with no parameters as a way to synchronize the boards."""

        # logger.info("Sending %s in %s bits...", value, length)

        # Send frames
        for bit in range(length):
            # logger.info("Sending %s", bit)
            # logger.info("Send bit %s: %s", bit, value & 2**bit != 0)
            self._handshake_send()
            # print(end="0")
            self.gpio.value = False
            delay_us(self.tick_send)
            # print(end="?")
            self.gpio.value = value & 2**bit != 0
            delay_us(self.tick_send * 2)
            # print(end="1")
            self.gpio.value = True
            delay_us(self.tick_send)
            # print(end="p")
            self._ping()
            # print()
        # logger.info("Data sent")

    def receive(self, length: int = 1) -> int:
        """Receive data

        Can be called with no parameters as a way to synchronize the boards."""
        # logger.info("Receiving %s bits", length)
        self.gpio.switch_to_input(digitalio.Pull.UP)

        value = 0

        # Receive frames
        for bit in range(length):
            count0 = 0
            count1 = 1
            # logger.info("Reading %s", bit)
            self._handshake_receive()

            # print(end="?")
            self._wait_for(False)

            # while self.gpio.value == False:
            #     count0 += 1
            # while self.gpio.value == True:
            #     count1 += 1

            # delay_us(self.tick_send)
            # for _ in range(2 * self.tick_send // self.tick_read):
            #     if self.gpio.value == False:
            #         count0 += 1
            #     else:
            #         count1 += 1

            for _ in range(4 * self.tick_send // self.tick_read):
                if self.gpio.value == False:
                    count0 += 1
                if self.gpio.value == True:
                    count1 += 1
                delay_us(self.tick_read)

            # print(end="p")
            # self._wait_for(False)
            self._wait_for(True)

            # logger.info("Read %s: %s (%s/%s)", bit, count1 > count0, count0, count1)
            value |= (count1 > count0) * 2**bit

        self.gpio.switch_to_output(True, digitalio.DriveMode.OPEN_DRAIN)

        # logger.info("Received: %s", value)
        # if (length == 8 and value != 12) or (length == 6 and value != 0):
        #     raise RuntimeError("Bad value")
        return value
