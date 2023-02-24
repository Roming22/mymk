from seaks.buffer import Buffer


class Action:
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
    def oneshot(cls, key_name) -> "Action":
        def func():
            print(f"Press and release {key_name} switch")
            Buffer.add(key_name, True)
            Buffer.add(key_name, False)
            return True

        return cls(func)

    @classmethod
    def press(cls, key_name) -> "Action":
        if key_name is None:
            return cls.noop()

        def func():
            print(f"Press {key_name} switch")
            Buffer.add(key_name, True)
            return True

        return cls(func)

    @classmethod
    def release(cls, key_name) -> "Action":
        if key_name is None:
            return cls.noop()

        def func():
            print(f"Release {key_name} switch")
            Buffer.add(key_name, False)
            return True

        return cls(func)

    @classmethod
    def state(cls, statemachine, state_name) -> "Action":
        def func():
            statemachine.activate_state(statemachine.states[state_name])
            return True

        return Action(func)
