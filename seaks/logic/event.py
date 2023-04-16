import time

from seaks.logic.buffer import Buffer
from seaks.utils.memory import memory_cost


class Timer:
    instances: dict[str, "Timer"] = {}

    running = set()

    @memory_cost("Timer")
    def __init__(self, name: str, seconds: float) -> None:
        if name in Timer.instances.keys():
            raise RuntimeError(
                "You cannot instanciate the same object twice. Use get() instead."
            )
        print("Timer:", name, f", {seconds}s,", name)
        self.seconds = seconds
        self.name = name
        Timer.instances[name] = self

    @classmethod
    def get(cls, name: str) -> "Timer":
        return cls.instances[name]

    @classmethod
    def start(cls, name):
        # print(f"    Timer: {name} starting")
        timer = cls.instances[name]
        cls.running.add(name)
        timer.reset(name)

    @classmethod
    def reset(cls, name):
        timer = cls.instances[name]
        timer.end_at = time.monotonic_ns() + timer.seconds * 10**9

    @classmethod
    def stop(cls, name):
        # print(f"    Timer: {name} stopping")
        Timer.running.remove(name)

    def is_expired(self):
        if self.end_at and self.end_at <= time.monotonic_ns():
            Timer.stop(self.name)
            return True
        return False

    @classmethod
    def tick(cls):
        # print("Timers ticking")
        for timer_name in cls.running:
            timer = Timer.instances[timer_name]
            if timer.is_expired():
                Buffer.register(timer_name)
