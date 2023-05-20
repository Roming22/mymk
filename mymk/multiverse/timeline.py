class Timeline:
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
        self.parent = parent
        self.children = []

        self.events = events
        if parent:
            self.output = list(parent.output)
            parent.children.append(self)
        else:
            self.determined = True
            self.output = []
        self.determined = False
        self.next_timeline = None

    def check_is_determined(self):
        # Timeline conditions are satisfied
        if self.parent and len(self.events) == 0:
            self.determined = True
            self.parent.next_timeline = self
            # TODO: Start a new timeline.
            # The current layer should be able to instanciate it.

    def prune(self):
        """Some timelines might be deadends. They are removed from the multiverse"""
        parent = self.parent
        if parent:
            parent.children.remove(self)
            if not parent.children:
                parent.prune()
