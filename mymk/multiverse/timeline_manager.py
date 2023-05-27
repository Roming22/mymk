import time

from mymk.feature.layers.layer_manager import LayerManager
from mymk.multiverse.timeline import Timeline
from mymk.utils.memory import memory_cost
from mymk.utils.time import pretty_print, time_it


class TimelineManager:
    _universes = []
    _time_last_event = time.monotonic_ns()

    def __init__(self, timeline=False) -> None:
        if not timeline:
            timeline = Timeline()
        self.active_timelines = [timeline]
        self.timeline_start = timeline
        self.current_timeline = timeline
        TimelineManager._universes.append(self)

    @classmethod
    def activate(cls, layer_name: str) -> None:
        universe = TimelineManager()
        print("Universes:", len(cls._universes))
        for universe in cls._universes:
            for timeline in universe.active_timelines:
                universe.current_timeline = timeline
                LayerManager.activate(layer_name, timeline)

    def split(self, events) -> Timeline:
        """Create new timelines"""
        print("timeline definition", events)
        new_timeline = Timeline(events, self.current_timeline)
        self.active_timelines.append(new_timeline)
        new_timeline.check_is_determined()

        if not self.current_timeline.determined:
            self.current_timeline.determined = True
            self.active_timelines.remove(self.current_timeline)
        if self.current_timeline.parent:
            self.current_timeline.parent.next_timeline = self.current_timeline
        return new_timeline

    def mark_determined(self) -> None:
        self.current_timeline.determined = True
        self.current_timeline.parent.next_timeline = self.current_timeline

    def _process_event(self, event) -> None:
        """Process an event

        The event is checked against the timeline expectation.
        If the event is not part of the timeline, the timeline is terminated.
        If the event is part of the timeline, the associated action is executed.
        """
        timeline = self.current_timeline
        print("Processing timeline")

        # Process an event as part of a group of event.
        try:
            data = timeline.events.pop(event)
            _, action, output = data.pop(0)
            if data:
                print("Follow-up", data)
                timeline.events[data[0][0]] = data
            if action:
                print("Immediate action")
                action()
            if output:
                print("Output action")
                timeline.output.append(output)
            return
        except KeyError:
            pass

        # Process a press event as an interrupt
        if not event.startswith("!") and not event.startswith("timer."):
            try:
                data = timeline.events.pop("interrupt")
                print("Interrupt", data)
                _, action, output = data.pop(0)
                if data:
                    print("Follow-up", data)
                    timeline.events[data[0][0]] = data
                if action:
                    print("Immediate action")
                    action()
                if output:
                    print("Output action")
                    timeline.output.append(output)
            except KeyError:
                pass

        # Process the event as an event triggering a new timeline
        try:
            timelines_events = timeline.layer.load_events(self, event)
        except KeyError:
            if timeline.events:
                print("Deadend")
                self.active_timelines.remove(timeline)
                timeline.prune()
            else:
                print("Unknown")
            return

        print("New timelines:", timelines_events)
        for timeline_events in timelines_events:
            print(timeline_events)
            event_definitions = dict(timeline.events)
            event_definitions[event] = timeline_events
            new_timeline = self.split(event_definitions)
            self.current_timeline = new_timeline
            self._process_event(event)
            self.current_timeline = timeline

        timeline.check_is_determined()

    @classmethod
    @memory_cost("Process", True)
    @time_it
    def process_event(cls, event) -> None:
        """Process an event in all active timelines

        That event might trigger a timeline resolution, in which case
        the timelines resolving the sequence of events is collapsed
        into a single timeline, and the timeline is executed if it is
        the best solution for the chain of events.
        """
        print("\n" * 3)
        print(" ".join(["#", event, "#" * 100])[:120])
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
            self.active_timelines.clear()
            self.active_timelines.append(self.timeline_start)
            self.timeline_start.parent = None
            self.current_timeline = self.timeline_start
            # The new timeline might already be resolved
            self.resolve()

        if self.current_timeline == self.timeline_start:
            for action in self.timeline_start.output:
                action()
            self.timeline_start.output.clear()
