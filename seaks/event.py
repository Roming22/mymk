from seaks.state import StateMachine


class Event:
    def __init__(self, timestamp, object, value) -> None:
        self.timestamp = timestamp
        self.object = object
        self.value = value

    def __repr__(self):
        mseconds = self.timestamp % 1000
        seconds = (self.timestamp // 1000) % 60
        minutes = ((self.timestamp // 1000) // 60) % 60
        hours = (self.timestamp // 1000) // 3600
        return f"[{hours:02d}:{minutes:02d}:{seconds:02d}.{mseconds:03d}] {self.object}: {self.value}"

    @staticmethod
    def notify(object, value, timestamp):
        event = Event(timestamp, object, value)
        StateMachine.register_event(event)
