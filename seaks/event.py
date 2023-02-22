import time


class Event:
    _queue = []

    def __init__(self, trigger, timestamp) -> None:
        if timestamp is None:
            timestamp = int(time.monotonic() * 1000)
        self.timestamp = timestamp
        self.trigger = trigger

    def __repr__(self):
        mseconds = self.timestamp % 1000
        seconds = (self.timestamp // 1000) % 60
        minutes = ((self.timestamp // 1000) // 60) % 60
        hours = (self.timestamp // 1000) // 3600
        return (
            f"[{hours:02d}:{minutes:02d}:{seconds:02d}.{mseconds:03d}] {self.trigger}"
        )

    @classmethod
    def register(cls, trigger, timestamp=None):
        event = Event(trigger, timestamp)
        cls._queue.append(event)

    @classmethod
    def get_next(cls):
        try:
            return cls._queue.pop(0)
        except IndexError:
            return None


class Trigger:
    def __init__(self, object, value) -> None:
        self.object = object
        self.value = value
        self.__hash = hash(f"{self}")

    def __repr__(self):
        return f"{self.object}: {self.value}"

    def __eq__(self, __o: object) -> bool:
        return self.__hash__() == __o.__hash__()

    def __hash__(self) -> int:
        return self.__hash

    def fire(self):
        Event.register(self)


class Timer:
    timers = []

    def __init__(self, trigger, seconds) -> None:
        self.trigger = trigger
        self.end_time = time.monotonic() + seconds
        Timer.timers.append(self)

    def is_expired(self):
        return self.end_time <= time.monotonic()

    @classmethod
    def tick(cls):
        timers = []
        for timer in cls.timers:
            if timer.is_expired():
                timer.trigger.fire()
            else:
                timers.append(timer)
        cls.timers = timers
