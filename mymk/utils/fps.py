from mymk.utils.logger import logger
from mymk.utils.memory import get_usage
from mymk.utils.time import Time

_counter = 0
_refresh_rate = 1
_time = 0


def display() -> None:
    global _counter
    global _refresh_rate
    logger.info("\n[FPS] %s", int(_counter / _refresh_rate))
    reset()


def start(refresh_rate: int) -> None:
    global _refresh_rate
    _refresh_rate = refresh_rate
    reset()


def reset() -> None:
    global _counter
    global _time
    _counter = 0
    _time = Time.tick_time + _refresh_rate * 10**9


def tick(check_memory: bool = False) -> None:
    global _counter
    global _time
    _counter += 1
    now = Time.tick_time
    if now >= _time:
        display()
        if check_memory:
            logger.info("[Memory]%s", get_usage(True))
