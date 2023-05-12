import time

import seaks.logic.event_handler as EventHandler
from seaks.utils.memory import memory_cost


class Timer:
    instances: dict[str, "Timer"] = {}

    running = set()

    @memory_cost("Timer")
    def __init__(self, name: str) -> None:
        if name in Timer.instances.keys():
            raise RuntimeError(
                "You cannot instanciate the same object twice. Use get() instead."
            )
        print("Timer:", name)
        self.name = name
        Timer.instances[name] = self

    @classmethod
    def get(cls, name: str) -> "Timer":
        try:
            return cls.instances[name]
        except KeyError:
            return cls(name)

    @classmethod
    def start(cls, name: str, delay: float) -> None:
        # print(f"    Timer: {name} starting", delay)
        timer = cls.get(name)
        cls.running.add(name)
        timer.end_at = time.monotonic_ns() + delay * 10**9

    @classmethod
    def stop(cls, name) -> None:
        # print(f"    Timer: {name} stopping")
        try:
            Timer.running.remove(name)
        except KeyError:
            pass

    def is_expired(self) -> bool:
        if self.end_at and self.end_at <= time.monotonic_ns():
            Timer.stop(self.name)
            return True
        return False

    @classmethod
    def tick(cls) -> None:
        # print("Timers ticking")
        for timer_name in cls.running:
            timer = Timer.instances[timer_name]
            if timer.is_expired():
                EventHandler.handle_event(timer_name)
