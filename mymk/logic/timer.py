from mymk.utils.logger import logger

# from mymk.utils.memory import memory_cost
# from mymk.utils.time import pretty_print, time_it
from mymk.utils.time import Time


class Timer:
    __slots__ = ("running", "name", "end_at", "timeline", "universe")
    running: list["Timer"] = []

    # @memory_cost("Timer")
    def __init__(self, name: str, delay: float, universe, timeline) -> None:
        # logger.debug("Timer: %s", name)
        self.name = name
        self.end_at = Time.tick_time + int(delay * 10**9)
        self.timeline = timeline
        self.universe = universe
        Timer.running.append(self)
        # logger.debug("Timer starting at %s, ending at %s", Time.tick_time, self.end_at)

    def stop(self) -> None:
        # logger.debug(f"    Timer: %s stopping", self.name)
        try:
            Timer.running.remove(self)
        except KeyError:
            pass

    def is_expired(self) -> bool:
        return self.end_at <= Time.tick_time

    # @time_it
    def process_event(self) -> None:
        if self.timeline.parent is not None:
            logger.debug("#" * 120)
            logger.debug("# %s", self.name)
            logger.debug("#" * 120)
            self.universe._process_event(self.timeline, self.name)
            self.universe.resolve()
            logger.debug(
                "[%s] After: %s",
                self.timeline.what,
                self.universe.print_active_timelines(),
            )
        self.stop()

    @classmethod
    def tick(cls) -> None:
        if not cls.running:
            return
        # logger.debug("Timers ticking")
        for timer in list(cls.running):
            if timer.is_expired():
                # logger.debug("Time: %s", Time.tick_time)
                timer.process_event()
