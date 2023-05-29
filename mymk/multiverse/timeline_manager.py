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
            timeline = Timeline({})
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

        if self.current_timeline in self.active_timelines:
            self.active_timelines.remove(self.current_timeline)

        new_timeline = Timeline(events, self.current_timeline)
        self.active_timelines.append(new_timeline)

        return new_timeline

    def mark_determined(self) -> None:
        self.current_timeline.determined = True
        self.current_timeline.parent.next_timeline = self.current_timeline

    def _process_event_in_timeline(self, event) -> None:
        timeline = self.current_timeline
        data = timeline.events.pop(event)
        print("\n## Continuing timeline:", self.current_timeline)
        _, action, output = data.pop(0)
        if data:
            print("Follow-up", data)
            timeline.events[data[0][0]] = data
        if action:
            # print("Immediate action")
            action()
        if output:
            # print("Output action")
            timeline.output.append(output)

    def _process_interrupt_in_timeline(self) -> None:
        timeline = self.current_timeline
        data = timeline.events["interrupt"]
        print("## Interrupt:", self.current_timeline)
        _, action, output = data.pop(0)
        if action:
            # print("Immediate action")
            action()
        if output:
            # print("Output action")
            timeline.output.append(output)
        timeline.events[data[0][0]] = data

    def _event_is_interrupt(self, event) -> bool:
        timeline = self.current_timeline
        if not timeline.events:
            return False
        if event.startswith("!"):
            return False
        if event.startswith("timer"):
            return False
        return True

    def _process_event(self, event) -> None:
        """Process an event

        The event is checked against the timeline expectation.
        If the event is not part of the timeline, the timeline is terminated.
        If the event is part of the timeline, the associated action is executed.
        """
        timeline = self.current_timeline

        if timeline.events:
            # Process an event as part of a group of event.
            try:
                self._process_event_in_timeline(event)
                return
            except KeyError:
                pass

            # Process a press event as an interrupt
            if self._event_is_interrupt(event) and not timeline.determined:
                try:
                    self._process_interrupt_in_timeline()
                except KeyError:
                    print("## Deadend:", timeline)
                    self.active_timelines.remove(timeline)
                    timeline.prune()
                    return

        # Process the event as an event triggering a new timeline
        if not timeline.determined:
            print("## Deadend:", timeline)
            self.active_timelines.remove(timeline)
            timeline.prune()
            return
        try:
            timelines_events = timeline.layer.load_events(self, event)
        except KeyError:
            if timeline.events:
                print("## Deadend:", timeline)
                self.active_timelines.remove(timeline)
                timeline.prune()
            else:
                raise RuntimeError("Unknown event sequence")
            return

        print("\n## New timelines:", self.current_timeline)
        new_timelines = []
        for timeline_events in timelines_events:
            # print(timeline_events)
            new_timelines.append(self.split(timeline_events))
        for self.current_timeline in new_timelines:
            self._process_event(event)

        print(self.active_timelines)

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
        if (
            self.timeline_start.output
            and self.current_timeline == self.timeline_start
            and self.timeline_start.output
        ):
            print("Running actions")
            for action in self.timeline_start.output:
                action()
            self.timeline_start.output.clear()

        if self.timeline_start.children and False not in [
            t.determined for t in self.timeline_start.children
        ]:
            print("Resolving timelines")
            self.timeline_start = self.timeline_start.next_timeline
            self.timeline_start.parent = None
            self.current_timeline = self.timeline_start
            # The new timeline might already be resolved
            self.resolve()
