from mymk.multiverse.timeline import Timeline
from mymk.utils.logger import logger
# from mymk.utils.memory import memory_cost
# from mymk.utils.time import Time, pretty_print, time_it


class TimelineManager:
    _universes = []

    def __init__(self, timeline=False) -> None:
        if not timeline:
            timeline = Timeline("begin")
        self.timeline_start = timeline
        self.current_timeline = timeline
        TimelineManager._universes.append(self)

    @classmethod
    def activate(cls, layer_name: str, is_root: bool = True) -> None:
        universe = TimelineManager()
        logger.info("Universes: %s", len(cls._universes))
        for universe in cls._universes:
            for timeline in universe.get_active_timelines():
                timeline.activate(layer_name, True)

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

    def print_active_timelines(self):
        timelines = []
        for timeline in self.get_active_timelines():
            uid = f"\n  * {timeline.what}"
            timelines.append(uid)
        return "".join(timelines)

    def split(self, what) -> Timeline:
        """Create new timelines"""
        new_timeline = Timeline(what, self.current_timeline)
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
            self.delete_timeline(parent)

    def _process_event_in_timeline(self, event) -> None:
        timeline = self.current_timeline
        data = timeline.events.pop(event)
        # logger.debug("\n## Continuing timeline: %s", self.current_timeline)
        _, actions, output = data.pop(0)
        if data:
            # logger.debug("Follow-up %s", data)
            timeline.events[data[0][0]] = data
        for action in actions:
            # logger.debug("Immediate action")
            action()
        if output:
            # logger.debug("Output action")
            timeline.output.extend(output)

    def _process_event(self, timeline, event) -> None:
        """Process an event

        The event is checked against the timeline expectation.
        If the event is not part of the timeline, the timeline is terminated.
        If the event is part of the timeline, the associated action is executed.
        """
        logger.info("## %s", timeline.what)
        logger.info("Before: %s", self.print_active_timelines())

        self.current_timeline = timeline

        new_children = 0
        if timeline.events:
            # Process an event as part of a group of event.
            try:
                self._process_event_in_timeline(event)
                return
            except KeyError:
                pass

            # Process a press event as an interrupt
            if (
                timeline.events
                and event.startswith("board.")
                and not timeline.determined
            ):
                try:
                    new_children = len(timeline.children)
                    self._process_event_in_timeline("interrupt")
                    new_children = len(timeline.children) - new_children
                except KeyError:
                    # logger.debug("## Deadend: %s", timeline)
                    self.delete_timeline(timeline)
                    return

        # Process the event as an event triggering a new timeline
        if not timeline.determined:
            # logger.debug("## Deadend: %s", timeline)
            self.delete_timeline(timeline)
            return
        try:
            if new_children:
                for child in timeline.children[-new_children:]:
                    self.current_timeline = child
                    child.load_events(self, event)
                self.current_timeline = child.parent
            else:
                timeline.load_events(self, event)
        except KeyError:
            if timeline.events:
                # logger.debug("## Deadend: %s", timeline)
                self.delete_timeline(timeline)
            else:
                raise RuntimeError("Unknown event sequence")

    @classmethod
    # @memory_cost("Process", True)
    # @time_it
    def process_event(cls, event) -> None:
        """Process an event in all active timelines

        That event might trigger a timeline resolution, in which case
        the timelines resolving the sequence of events is collapsed
        into a single timeline, and the timeline is executed if it is
        the best solution for the chain of events.
        """
        logger.info("\n" * 3)
        logger.info(" ".join(["#", event, "#" * 100])[:120])

        # Send event to all timelines
        for universe in cls._universes:
            for timeline in universe.get_active_timelines():
                universe._process_event(timeline, event)
            universe.resolve()
            logger.info("After: %s", universe.print_active_timelines())

    def resolve(self) -> None:
        """Solve split timelines"""
        if self.timeline_start.output and self.current_timeline == self.timeline_start:
            for action in self.timeline_start.output:
                action()
            self.timeline_start.output.clear()
            if not self.timeline_start.events:
                self.timeline_start.what = "begin"

        if self.timeline_start.children and False not in [
            t.determined for t in self.timeline_start.children
        ]:
            self.timeline_start = self.timeline_start.next_timeline
            self.timeline_start.parent = None
            self.current_timeline = self.timeline_start
            # The new timeline might already be resolved
            self.resolve()
