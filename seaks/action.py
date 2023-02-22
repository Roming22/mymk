from adafruit_hid.keycode import Keycode


class Action:
    def __init__(self, callback) -> None:
        self.callback = callback

    def run(self) -> None:
        # print("Running action")
        self.callback()

    @classmethod
    def noop(cls):
        def func() -> bool:
            return True

        return cls(func)

    @classmethod
    def oneshot(cls, kbd, key) -> "Action":
        if key is None:
            return cls.noop()

        kc = getattr(Keycode, key)

        def func():
            print(f"Press and release {key}")
            kbd.press(kc)
            kbd.release(kc)
            return True

        return cls(func)

    @classmethod
    def press(cls, kbd, key) -> "Action":
        if key is None:
            return cls.noop()

        kc = getattr(Keycode, key)

        def func():
            print(f"Press {key}")
            kbd.press(kc)
            return True

        return cls(func)

    @classmethod
    def release(cls, kbd, key) -> "Action":
        if key is None:
            return cls.noop()

        kc = getattr(Keycode, key)

        def func():
            print(f"Release {key}")
            kbd.release(kc)
            return True

        return cls(func)

    @classmethod
    def state(cls, statemachine, state_name) -> "Action":
        def func():
            statemachine.activate_state(statemachine.states[state_name])
            return True

        return Action(func)
