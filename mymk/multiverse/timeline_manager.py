import time

from mymk.multiverse.timeline import Timeline
from seaks.utils.time import pretty_print, time_it


class TimelineManager:
    _universes = []
    _time_last_event = time.monotonic_ns()

    def __init__(self):
        self.active_timelines = None
        self.timeline_start = None
        self.current_timeline = None
        TimelineManager._universes.append(self)

    def start(self, timeline) -> None:
        self.active_timelines = [timeline]
        self.timeline_start = timeline
        self.current_timeline = None

    def split(self, timeline_definitions):
        """Create new timelines

        The timeline_definition is a dictionary with 3 keys:
            events:
        """
        for definition in timeline_definitions:
            events = definition["events"]
            new_timeline = Timeline(events, self.current_timeline)
            self.active_timelines.append(new_timeline)
            if action := definition.get("action"):
                action()
            if action := definition.get("output"):
                new_timeline.output.append(action)
            new_timeline.check_is_determined()

        self.current_timeline.determined = True
        self.active_timelines.remove(self.current_timeline)
        if self.current_timeline.parent:
            self.current_timeline.parent.next_timeline = self.current_timeline

    def _process_event(self, event) -> None:
        """Process an event

        The event is checked against the timeline expectation.
        If the event is not part of the timeline, the timeline is terminated.
        If the event is part of the timeline, the associated action is executed.
        """
        timeline = self.current_timeline
        # TODO: Workaround until a new timeline is created by check_is_determined()
        if not timeline.events:
            return

        expected_event, action, output = timeline.events.pop(0)
        if event != expected_event:
            self.active_timelines.remove(timeline)
            timeline.prune()
            return
        if action:
            action()
        if output:
            timeline.output.append(output)
        timeline.check_is_determined()

    @classmethod
    @time_it
    def process_event(cls, event):
        """Process an event in all active timelines

        That event might trigger a timeline resolution, in which case
        the timelines resolving the sequence of events is collapsed
        into a single timeline, and the timeline is executed if it is
        the best solution for the chain of events.
        """
        print(" ".join(["\n\n\n#", event, "#" * 100])[:120])
        now = time.monotonic_ns()
        print("# At:", pretty_print(now), f"(+{(now-cls._time_last_event)/10**6}ms)")
        cls._time_last_event = now

        # Send event to all timelines
        for universe in cls._universes:
            for timeline in list(universe.active_timelines):
                universe.current_timeline = timeline
                universe._process_event(event)
            universe.resolve()

    def resolve(self) -> None:
        """Solve split timelines"""
        if self.timeline_start.children and False not in [
            t.determined for t in self.timeline_start.children
        ]:
            print("Resolving timelines")
            self.timeline_start = self.timeline_start.next_timeline
            for action in self.timeline_start.output:
                action()
            self.timeline_start.output.clear()
            self.active_timelines.clear()
            self.active_timelines.append(self.timeline_start)
            self.timeline_start.parent = None
            # The new timeline might already be resolved
            self.resolve()
