import time


class FPS:
    counter = 0
    refresh_rate = 1
    time = 0

    @classmethod
    def display(cls):
        print(f"FPS: {int(cls.counter/cls.refresh_rate)}")
        cls.reset()

    @classmethod
    def start(cls, refresh_rate):
        cls.refresh_rate = refresh_rate
        cls.reset()

    @classmethod
    def reset(cls):
        cls.counter = 0
        cls.time = time.monotonic() + cls.refresh_rate

    @classmethod
    def tick(cls):
        cls.counter += 1
        now = time.monotonic()
        if now >= cls.time:
            cls.display()
