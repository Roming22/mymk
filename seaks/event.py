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
    timers = dict()
    running_timers = set()

    def __init__(self, trigger, seconds, name, start=False) -> None:
        print("Timer:", trigger, f", {seconds}s,", name)
        self.trigger = trigger
        self.seconds = seconds
        self.name = name
        Timer.timers[name] = self
        if start:
            self.start(name)

    @classmethod
    def start(cls, name):
        timer = cls.timers[name]
        cls.running_timers.add(timer.name)
        timer.reset(name)

    @classmethod
    def reset(cls, name):
        timer = cls.timers[name]
        timer.end_at = time.monotonic_ns() + timer.seconds * 10**9

    @classmethod
    def stop(cls, name):
        Timer.running_timers.remove(name)

    def is_expired(self):
        if self.end_at and self.end_at <= time.monotonic_ns():
            Timer.stop(self.name)
            return True
        return False

    @classmethod
    def get(cls, key):
        return cls.timers.get(key, None)

    @classmethod
    def tick(cls):
        for timer_name in cls.running_timers:
            timer = Timer.timers[timer_name]
            if timer.is_expired():
                timer.trigger.fire()
