class Timeline:
    active_timelines = []
    next_timeline = None

    def __init__(self, events, output=[], status=False) -> None:
        """Create a new timeline

        events: an ordered list of expected events in the timeline. Each event
                is paired with the action that should be executed when the event
                is triggered.
                The timeline will be terminated if it receives an event that is
                not part of the timeline.
        output: an order list of actions that will be executed if the timeline
                is selected when all the timeline are resolved time.
        status: a boolean flag that indicates whether the timeline has come to
                some sort of resolution. This usually means that a character has
                been output or there was a layer change.
                A resolved timeline will tend to spawn new timelines.
        """
        self.events = events
        if output:
            self.output = list(output)
        else:
            self.output = output
        self.status = status
        self.active_timelines.append(self)

    def split(self) -> list:
        """Create a new timeline"""
        new_timeline = Timeline(self.events, self.output, self.status)
        return [self, new_timeline]

    def _process_event(self, event) -> None:
        """Process an event

        The event is checked against the timeline expectation.
        If the event is not part of the timeline, the timeline is terminated.
        If the event is part of the timeline, the associated action is executed.
        """
        print("GRNX", self.events)
        expected_event, action = self.events.pop(0)
        if event != expected_event:
            self.active_timelines.remove(self)
        if action:
            action()

    @classmethod
    def process_event(cls, event):
        """Process an event in all active timelines

        That event might trigger a timeline resolution, in which case
        the timeline resolving the sequence of events is executed.
        """
        for timeline in list(cls.active_timelines):
            timeline._process_event(event)
        if False not in [t.status for t in cls.active_timelines]:
            cls.collapse()

    @classmethod
    def resolve(cls):
        """Execute the action of the timeline and collapse the multiverse to a single point"""
        print("Resolving timelines")
        timeline = cls.next_timeline
        for action in timeline.output:
            action()
        timeline.output.clear()
        cls.active_timeline = [timeline]
