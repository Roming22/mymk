import neopixel


class NeoPixel(neopixel.NeoPixel):
    _instances = {}

    def __init__(
        self, uid, pin: str, count: int = 1, color: tuple[int] = (255, 255, 255)
    ) -> None:
        super().__init__(pin, count)
        self.fill(color)
        NeoPixel._instances[uid] = self
