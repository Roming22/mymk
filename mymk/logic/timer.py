from mymk.utils.memory import memory_cost
from mymk.utils.time import Time, pretty_print, time_it
from mymk.utils.toolbox import debug

class Timer:
    running: list["Timer"] = []

    # @memory_cost("Timer")
    def __init__(self, name: str, delay: float, universe, timeline) -> None:
        # debug("Timer:", name)
        self.name = name
        self.delay = delay
        self.end_at = Time.tick_time + self.delay * 10**9
        self.timeline = timeline
        self.universe = universe
        Timer.running.append(self)

    def stop(self) -> None:
        # debug(f"    Timer: {self.name} stopping")
        try:
            Timer.running.remove(self)
        except KeyError:
            pass

    def is_expired(self) -> bool:
        is_expired = self.timeline.parent is None or self.end_at <= Time.tick_time
        if is_expired:
            self.stop()
        return is_expired

    @time_it
    def process_event(self):
        debug("\n" * 3)
        debug(" ".join(["#", self.name, "#" * 100])[:120])
        now = Time.tick_time
        debug(
            "# At:",
            pretty_print(now),
        )
        self.universe.process_timer(self.timeline, self.name)
        self.universe.resolve()
        # debug("After:", self.universe.print_active_timelines())

    @classmethod
    def tick(cls) -> None:
        if not cls.running:
            return
        # debug("Timers ticking")
        for timer in list(cls.running):
            if timer.is_expired():
                timer.process_event()
