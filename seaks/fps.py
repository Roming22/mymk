import time

from seaks.action import Action
from seaks.event import Timer, Trigger
from seaks.state import StateMachine


class FPS:
    counter = 0
    refresh_rate = 1
    trigger = Trigger("timer.fps", True)
    time = 0

    @classmethod
    def display(cls):
        print(f"FPS: {int(cls.counter/cls.refresh_rate)}")
        cls.reset()

    @classmethod
    def start(cls, refresh_rate):
        fps = StateMachine("FPS")
        fps.new_state("display")
        fps.activate_state(fps.states["display"])
        fps.states["display"].add_trigger(
            Trigger("timer.fps", True),
            Action(FPS.display),
        )

        cls.refresh_rate = refresh_rate
        cls.reset()

    @classmethod
    def reset(cls):
        cls.counter = 0
        cls.time = time.monotonic()
        Timer(cls.trigger, cls.refresh_rate)

    @classmethod
    def tick(cls):
        cls.counter += 1
