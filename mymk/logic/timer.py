import time

from mymk.utils.memory import memory_cost
from mymk.utils.time import pretty_print, time_it


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
        self.timeline = None

    def start(self) -> None:
        # print(f"    Timer: {self.name} starting", self.delay)
        if not Timer.running:
            Timer.now = time.monotonic_ns()
        Timer.running.append(self)
        self.end_at = Timer.now + self.delay * 10**9
        self.timeline = self.universe.current_timeline

    def stop(self) -> None:
        # print(f"    Timer: {self.name} stopping")
        try:
            Timer.running.remove(self)
        except KeyError:
            pass

    def is_expired(self) -> bool:
        return self.end_at and self.end_at <= Timer.now

    @time_it
    def process_event(self):
        print("\n" * 3)
        print(" ".join(["#", self.name, "#" * 100])[:120])
        now = time.monotonic_ns()
        print("# At:", pretty_print(now))
        self.universe._process_event(self.timeline, self.name)
        self.stop()

    @classmethod
    def tick(cls) -> None:
        if not cls.running:
            return
        # print("Timers ticking")
        cls.now = time.monotonic_ns()
        for timer in list(cls.running):
            if timer.is_expired():
                timer.process_event()
