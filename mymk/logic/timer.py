from mymk.utils.memory import memory_cost
from mymk.utils.time import Time, pretty_print, time_it


class Timer:
    running: list["Timer"] = []

    # @memory_cost("Timer")
    def __init__(self, name: str, delay: float, universe, timeline) -> None:
        # print("Timer:", name)
        self.name = name
        self.delay = delay
        self.end_at = Time.tick_time + self.delay * 10**9
        self.timeline = timeline
        self.universe = universe
        Timer.running.append(self)

    def stop(self) -> None:
        # print(f"    Timer: {self.name} stopping")
        try:
            Timer.running.remove(self)
        except KeyError:
            pass

    def is_expired(self) -> bool:
        return self.end_at and self.end_at <= Time.tick_time

    @time_it
    def process_event(self):
        now = Time.tick_time
        if self.timeline.parent is not None:
            self.universe._process_event(self.timeline, self.name)
            self.universe.resolve()
            print("After:", self.universe.print_active_timelines())
        self.stop()

    @classmethod
    def tick(cls) -> None:
        if not cls.running:
            return
        # print("Timers ticking")
        for timer in list(cls.running):
            if timer.is_expired():
                timer.process_event()
