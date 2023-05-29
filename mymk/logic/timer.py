import time

from mymk.utils.memory import memory_cost


class Timer:
    now = 0
    running: list["Timer"] = []

    # @memory_cost("Timer")
    def __init__(self, name: str, delay: float, universe) -> None:
        # print("Timer:", name)
        self.delay = delay
        self.end_at = 0
        self.name = name
        self.universe = universe

    def start(self) -> None:
        # print(f"    Timer: {self.name} starting", self.delay)
        if not Timer.running:
            Timer.now = time.monotonic_ns()
        Timer.running.append(self)
        self.end_at = Timer.now + self.delay * 10**9

    def stop(self) -> None:
        # print(f"    Timer: {self.name} stopping")
        try:
            Timer.running.remove(self)
        except KeyError:
            pass

    def is_expired(self) -> bool:
        return self.end_at and self.end_at <= Timer.now

    @classmethod
    def tick(cls) -> None:
        if not cls.running:
            return
        # print("Timers ticking")
        cls.now = time.monotonic_ns()
        for timer in list(cls.running):
            if timer.is_expired():
                timer.universe.process_event(timer.name)
                timer.stop()
