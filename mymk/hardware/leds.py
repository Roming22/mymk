import neopixel

_instances = {}


def create(
    pin: str, count: int = 1, color: tuple[int] = (255, 255, 255)
) -> neopixel.NeoPixel:
    if pin not in _instances.keys():
        _instances[pin] = neopixel.NeoPixel(pin, count)
    pixels = _instances[pin]
    pixels.fill(color)
    return pixels
