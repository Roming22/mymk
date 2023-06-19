import neopixel


def create(pin: str, count: int = 1, color: tuple[int] = (255, 255, 255)) -> None:
    pixels = neopixel.NeoPixel(pin, count)
    pixels.fill(color)
    return pixels
