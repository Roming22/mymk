from seaks.hardware.keys import press, release


class Buffer:
    keystrokes = []

    @classmethod
    def add(cls, key_name, value):
        cls.keystrokes.append((key_name, value))

    @classmethod
    def flush(cls):
        for key_name, value in cls.keystrokes:
            if value:
                press(key_name)
            else:
                release(key_name)
        cls.keystrokes.clear()
