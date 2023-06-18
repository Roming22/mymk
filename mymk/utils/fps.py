from mymk.utils.time import Time

from mymk.utils.memory import get_usage


class FPS:
    counter = 0
    refresh_rate = 1
    time = 0

    @classmethod
    def display(cls) -> None:
        print(f"\n[FPS] {int(cls.counter/cls.refresh_rate)}")
        cls.reset()

    @classmethod
    def start(cls, refresh_rate: int) -> None:
        cls.refresh_rate = refresh_rate
        cls.reset()

    @classmethod
    def reset(cls) -> None:
        cls.counter = 0
        cls.time = Time.tick_time + cls.refresh_rate * 10**9

    @classmethod
    def tick(cls, check_memory=False) -> None:
        cls.counter += 1
        now = Time.tick_time
        if now >= cls.time:
            cls.display()
            if check_memory:
                print("[Memory]", get_usage(True))
