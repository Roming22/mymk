import time


class Event:
    _queue = []

    def __init__(self, trigger, timestamp) -> None:
        if timestamp is None:
            timestamp = time.monotonic_ns()
        self.timestamp = timestamp
        self.trigger = trigger

    def __repr__(self) -> None:
        useconds = self.timestamp % 10**9 // 1000
        seconds = (self.timestamp // 10**9) % 60
        minutes = ((self.timestamp // 10**9) // 60) % 60
        hours = (self.timestamp // 10**9) // 3600 % 24
        days = (self.timestamp // 10**9) // (3600 * 24)
        return f"[{days:03d} days, {hours:02d}:{minutes:02d}:{seconds:02d}.{useconds:06d}] {self.trigger}"

    @classmethod
    def register(cls, trigger, timestamp=None) -> None:
        event = Event(trigger, timestamp)
        cls._queue.append(event)

    @classmethod
    def get_queue(cls) -> list["Event"]:
        queue = cls._queue
        cls._queue = []
        return queue


class Trigger:
    def __init__(self, object, value) -> None:
        self.object = object
        self.value = value
        self.__hash = hash(f"{self}")

    def __repr__(self) -> None:
        return f"{self.object}: {self.value}"

    def __eq__(self, __o: object) -> bool:
        return self.__hash__() == __o.__hash__()

    def __hash__(self) -> int:
        return self.__hash

    def fire(self) -> None:
        Event.register(self)


class Timer:
    timers = []

    def __init__(self, trigger, seconds) -> None:
        self.trigger = trigger
        self.seconds = seconds * 10**9
        Timer.timers.append(self)
        self.reset()

    def is_expired(self):
        return self.end_at <= time.monotonic_ns()

    def reset(self):
        self.end_at = time.monotonic_ns() + self.seconds

    def stop(self):
        Timer.timers.remove(self)

    @classmethod
    def tick(cls):
        timers = []
        for timer in cls.timers:
            if timer.is_expired():
                timer.trigger.fire()
            else:
                timers.append(timer)
        cls.timers = timers
