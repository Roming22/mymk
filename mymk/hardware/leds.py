import neopixel

class Pixel:
    _instances = {}

    @classmethod
    def create(cls, pin: str, count: int = 1, color: tuple[int] = (255, 255, 255)) -> neopixel.NeoPixel:
        if pin not in cls._instances.keys():
            cls._instances[pin] = neopixel.NeoPixel(pin, count)
        pixels = cls._instances[pin]
        pixels.fill(color)
        return pixels
