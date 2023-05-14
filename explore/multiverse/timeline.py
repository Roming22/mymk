class Timeline:
    active_timelines = []
    timeline_start = None
    current_timeline = None

    def __init__(self, events, parent=None) -> None:
        """Create a new timeline

        events: an ordered list of expected events in the timeline. Each event
                is paired with the action that should be executed when the event
                is triggered, and an output action which is executed when the
                timeline is resolved.
                The timeline will be terminated if it receives an event that is
                not part of the timeline.
        output: an order list of actions that will be executed if the timeline
                is selected when all the timeline are resolved.
        determined: a boolean flag that indicates whether the timeline segment has
                come to some sort of resolution. This usually means that a character
                has been output or there was a layer change.
                A determined timeline will spawn new children timelines as
                new events are coming in.
        """
        cls = self.__class__
        self.parent = parent
        self.children = []

        self.events = events
        if parent:
            self.output = list(parent.output)
            parent.children.append(self)
        else:
            self.determined = True
            self.output = []
            cls.timeline_start = self
        cls.active_timelines.append(self)
        self.determined = False
        self.next_timeline = None

    @classmethod
    def split(cls, timeline_definitions):
        """Create new timelines

        The timeline_definition is a dictionary with 3 keys:
            events:
        """
        for definition in timeline_definitions:
            new_timeline = Timeline(definition["events"], cls.current_timeline)
            if action := definition.get("action"):
                action()
            if action := definition.get("output"):
                new_timeline.output.append(action)

        cls.current_timeline.determined = True
        cls.active_timelines.remove(cls.current_timeline)
        if cls.current_timeline.parent:
            cls.current_timeline.parent.next_timeline = cls.current_timeline

    def _process_event(self, event) -> None:
        """Process an event

        The event is checked against the timeline expectation.
        If the event is not part of the timeline, the timeline is terminated.
        If the event is part of the timeline, the associated action is executed.
        """
        expected_event, action, output = self.events.pop(0)
        if event != expected_event:
            self.__class__.active_timelines.remove(self)
            self.deadend()
        if action:
            action()
        if output:
            self.output.append(output)

        # Timeline conditions are satisfied
        if self.parent and len(self.events) == 0:
            self.determined = True
            self.parent.next_timeline = self

    def deadend(self):
        """Some timelines might be deadends. They are removed from the multiverse"""
        parent = self.parent
        if parent:
            parent.children.remove(self)
            if not parent.children:
                parent.deadend()

    @classmethod
    def process_event(cls, event):
        """Process an event in all active timelines

        That event might trigger a timeline resolution, in which case
        the timelines resolving the sequence of events is collapsed
        into a single timeline, and the timeline is executed if it is
        the best solution for the chain of events.
        """
        # Send event to all timelines
        for timeline in list(cls.active_timelines):
            cls.current_timeline = timeline
            timeline._process_event(event)
        cls.resolve()

    @classmethod
    def resolve(cls) -> None:
        """Solve split timelines"""
        if cls.timeline_start.children and False not in [
            t.determined for t in cls.timeline_start.children
        ]:
            print("Resolving timelines")
            cls.timeline_start = cls.timeline_start.next_timeline
            for action in cls.timeline_start.output:
                action()
            cls.timeline_start.output.clear()
            cls.active_timelines.clear()
            cls.active_timelines.append(cls.timeline_start)
            cls.timeline_start.parent = None
            # The new timeline might already be resolved
            cls.resolve()
