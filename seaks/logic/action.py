from seaks.hardware.keys import oneshot, press, release
from seaks.logic.event import Trigger
from seaks.utils.memory import memory_cost


class Action:
    @memory_cost("Action")
    def __init__(self, callback) -> None:
        self.callback = callback

    def run(self) -> None:
        # print("Running action")
        self.callback()

    @classmethod
    def noop(cls) -> "Action":
        def func() -> bool:
            return True

        return cls(func)

    @classmethod
    def chain(cls, *actions: "Action") -> "Action":
        def func() -> bool:
            for action in actions:
                action.run()
            return True

        return cls(func)

    @classmethod
    def oneshot(cls, key_name: str) -> "Action":
        def func():
            print(f"Press and release {key_name} switch")
            oneshot(key_name)()
            return True

        return cls(func)

    @classmethod
    def press(cls, key_name: str) -> "Action":
        if key_name is None:
            return cls.noop()

        def func():
            print(f"Press {key_name} switch")
            press(key_name)()
            return True

        return cls(func)

    @classmethod
    def release(cls, key_name: str) -> "Action":
        def func():
            print(f"Release {key_name} switch")
            release(key_name)()
            return True

        return cls(func)

    @classmethod
    def state(cls, statemachine: "StateMachine", state_name: str) -> "Action":
        def func():
            statemachine.activate_state(statemachine.states[state_name])
            return True

        return Action(func)

    @classmethod
    def trigger(cls, object: str, value):
        def func():
            Trigger(object, value).fire()
            return True

        return Action(func)
