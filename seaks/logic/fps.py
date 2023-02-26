import time


class FPS:
    counter = 0
    refresh_rate = 1
    time = 0

    @classmethod
    def display(cls) -> None:
        print(f"FPS: {int(cls.counter/cls.refresh_rate)}")
        cls.reset()

    @classmethod
    def start(cls, refresh_rate: int) -> None:
        cls.refresh_rate = refresh_rate
        cls.reset()

    @classmethod
    def reset(cls) -> None:
        cls.counter = 0
        cls.time = time.monotonic_ns() + cls.refresh_rate * 10**9

    @classmethod
    def tick(cls) -> None:
        cls.counter += 1
        now = time.monotonic_ns()
        if now >= cls.time:
            cls.display()
