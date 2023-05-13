class Timeline:
    active_timelines = []
    next_timeline = None

    def __init__(self, events, output=[], status=False) -> None:
        self.events = events
        if output:
            self.output = list(output)
        else:
            self.output = output
        self.status = status
        self.active_timelines.append(self)

    def split(self) -> list:
        new_timeline = Timeline(self.events, self.output, self.status)
        return [self, new_timeline]

    def _process_event(self, event) -> None:
        if event != self.events.pop(0):
            self.active_timeline.remove(self)

    @classmethod
    def process_event(cls, event):
        for timeline in list(cls.active_timelines):
            timeline._process_event(event)
        if False not in [t.status for t in cls.active_timelines]:
            cls.collapse()

    @classmethod
    def collapse(cls):
        print("Collapsing timelines")
        timeline = cls.next_timeline
        for action in timeline.output:
            action()
        timeline.output.clear()
        cls.active_timeline = [timeline]
    