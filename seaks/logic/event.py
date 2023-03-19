import time

from seaks.utils.memory import check_memory
from seaks.utils.time import pretty_print
from seaks.utils.toolbox import hash


class Event:
    _queue = []

    instances: dict[int, "Event"] = {}

    @check_memory("Event")
    def __init__(self, subject: str, value: "Any", uid: int) -> None:
        if id in Event.instances.keys():
            raise RuntimeError(
                "You cannot instanciate the same object twice. Use get() instead."
            )
        self.subject = subject
        self.value = value
        self.uid = uid
        Event.instances[uid] = self

    def __eq__(self, __o: object) -> bool:
        return self.__hash__() == __o.__hash__()

    def __hash__(self) -> int:
        return self.uid

    def __repr__(self) -> str:
        return f"{self.subject}: {self.value}"

    def fire(self) -> None:
        Event._queue.append((time.monotonic_ns(), self))

    @classmethod
    def get(cls, subject: str, value: "Any") -> "Event":
        uid = hash(f"{subject}: {value}")
        try:
            return cls.instances[uid]
        except KeyError:
            event = cls(subject, value, uid)
            return event

    @classmethod
    def get_next(cls) -> "Event":
        try:
            while data := cls._queue.pop(0):
                timestamp, event = data
                print(f"[{pretty_print(timestamp)}] {event}")
                yield event
        except IndexError:
            pass


class Timer:
    instances: dict[str, "Timer"] = {}

    running = set()

    @check_memory("Timer")
    def __init__(self, event: Event, seconds: float, name: str) -> None:
        if name in Timer.instances.keys():
            raise RuntimeError(
                "You cannot instanciate the same object twice. Use get() instead."
            )
        print("Timer:", event, f", {seconds}s,", name)
        self.event = event
        self.seconds = seconds
        self.name = name
        Timer.instances[name] = self

    @classmethod
    def get(cls, name: str) -> "Event":
        return cls.instances[name]

    @classmethod
    def start(cls, name):
        print(f"    Timer: {name} starting")
        timer = cls.instances[name]
        cls.running.add(timer.name)
        timer.reset(name)

    @classmethod
    def reset(cls, name):
        timer = cls.instances[name]
        timer.end_at = time.monotonic_ns() + timer.seconds * 10**9

    @classmethod
    def stop(cls, name):
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
                timer.event.fire()
