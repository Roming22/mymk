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
            timeline = Timeline({"what": "begin"})
        self.timeline_start = timeline
        self.current_timeline = timeline
        TimelineManager._universes.append(self)

    @classmethod
    def activate(cls, layer_name: str, is_root: bool = True) -> None:
        universe = TimelineManager()
        print("Universes:", len(cls._universes))
        for universe in cls._universes:
            for timeline in universe.get_active_timelines():
                layer = timeline.create_layer(layer_name)
                timeline.activate(layer, True)

    def get_active_timelines(self, timeline=None):
        if timeline is None:
            timeline = self.timeline_start
        timelines = []
        if timeline.children:
            for child in timeline.children:
                timelines += self.get_active_timelines(child)
        else:
            timelines.append(timeline)
        return timelines

    def split(self, events) -> Timeline:
        """Create new timelines"""
        new_timeline = Timeline(events, self.current_timeline)
        return new_timeline

    def mark_determined(self) -> None:
        self.current_timeline.determined = True
        if self.current_timeline.parent.next_timeline:
            self.delete_timeline(self.current_timeline.parent.next_timeline)
        self.current_timeline.parent.next_timeline = self.current_timeline

    def update_timeline(self, timeline, timeline_events) -> None:
        if timeline.children:
            for child in timeline.children:
                self.update_timeline(child, timeline_events)
        else:
            timeline.events.update(timeline_events)

    def delete_timeline(self, timeline):
        parent = timeline.parent
        timeline.prune()
        if parent and not parent.children:
            self.delete(parent)

    def _process_event_in_timeline(self, event) -> None:
        timeline = self.current_timeline
        data = timeline.events.pop(event)
        # print("\n## Continuing timeline:", self.current_timeline)
        _, action, output = data.pop(0)
        if data:
            # print("Follow-up", data)
            timeline.events[data[0][0]] = data
        if action:
            # print("Immediate action")
            action()
        if output:
            # print("Output action")
            timeline.output.append(output)

    def _process_interrupt_in_timeline(self) -> None:
        timeline = self.current_timeline
        data = timeline.events.pop("interrupt")
        # print("## Interrupt:", self.current_timeline)
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

    def _process_event(self, timeline, event) -> None:
        """Process an event

        The event is checked against the timeline expectation.
        If the event is not part of the timeline, the timeline is terminated.
        If the event is part of the timeline, the associated action is executed.
        """
        self.current_timeline = timeline

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
                    # print("## Deadend:", timeline)
                    self.delete_timeline(timeline)
                    return

        # Process the event as an event triggering a new timeline
        if not timeline.determined:
            # print("## Deadend:", timeline)
            self.delete_timeline(timeline)
            return
        try:
            timelines_events = timeline.load_events(self, event)
        except KeyError:
            if timeline.events:
                # print("## Deadend:", timeline)
                self.delete_timeline(timeline)
            else:
                raise RuntimeError("Unknown event sequence")
            return

        # print("\n## New timelines:", self.current_timeline)
        new_timelines = []
        for timeline_events in timelines_events:
            # print(timeline_events)
            new_timelines.append(self.split(timeline_events))
        for new_timeline in new_timelines:
            self._process_event(new_timeline, event)

    @classmethod
    # @memory_cost("Process", True)
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
            for timeline in universe.get_active_timelines():
                universe._process_event(timeline, event)
            universe.resolve()

    def resolve(self) -> None:
        """Solve split timelines"""
        if self.timeline_start.output and self.current_timeline == self.timeline_start:
            for action in self.timeline_start.output:
                action()
            self.timeline_start.output.clear()

        if self.timeline_start.children and False not in [
            t.determined for t in self.timeline_start.children
        ]:
            self.timeline_start = self.timeline_start.next_timeline
            self.timeline_start.parent = None
            self.current_timeline = self.timeline_start
            # The new timeline might already be resolved
            self.resolve()
