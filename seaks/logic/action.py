# from seaks.hardware.keys import oneshot, press, release
from seaks.logic.buffer import Buffer
from seaks.logic.event import Event
from seaks.utils.memory import check_memory


class Action:
    @check_memory("Action")
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
            # oneshot(key_name)()
            Buffer.register(f"{key_name}")
            Buffer.register(f"!{key_name}")
            return True

        return cls(func)

    @classmethod
    def press(cls, key_name: str) -> "Action":
        if key_name is None:
            return cls.noop()

        def func():
            print(f"Press {key_name} switch")
            # press(key_name)()
            Buffer.register(f"{key_name}")
            return True

        return cls(func)

    @classmethod
    def release(cls, key_name: str) -> "Action":
        def func():
            print(f"Release {key_name} switch")
            # release(key_name)()
            Buffer.register(f"!{key_name}")
            return True

        return cls(func)

    @classmethod
    def state(cls, statemachine: "StateMachine", state_name: str) -> "Action":
        def func():
            statemachine.activate_state(statemachine.states[state_name])
            return True

        return Action(func)

    @classmethod
    def trigger(cls, subject: str, value: "Any"):
        Event.get(subject, value)

        def func():
            Event.get(subject, value).fire()
            return True

        return Action(func)
