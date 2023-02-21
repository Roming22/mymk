from seaks.state import StateMachine


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

class Event:
    def __init__(self, timestamp, object, value) -> None:
        self.timestamp = timestamp
        self.trigger = Trigger(object,value)

    def __repr__(self):
        mseconds = self.timestamp % 1000
        seconds = (self.timestamp // 1000) % 60
        minutes = ((self.timestamp // 1000) // 60) % 60
        hours = (self.timestamp // 1000) // 3600
        return f"[{hours:02d}:{minutes:02d}:{seconds:02d}.{mseconds:03d}] {self.trigger}"

    @staticmethod
    def notify(object, value, timestamp):
        event = Event(timestamp, object, value)
        StateMachine.register_event(event)