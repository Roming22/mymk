from seaks.hardware.keys import oneshot, press, release


class Buffer:
    _instance: "Buffer" = None

    def __init__(self):
        self.keystrokes = []
        self.updated = False

        self.keys = {
            # Simple key
            "A": self.clear_after(press("A")),
            "a": self.clear_after(release("A")),
            # "B": self.clear_after(press("B")),
            # "b": self.clear_after(release("B")),
            # Chords
            "_+!": self.clear_after(lambda: True),
            # Combo
            "B+b": self.clear_after(oneshot("B")),
            "@+B+C": oneshot("G"),
            "C+c": self.clear_after(oneshot("C")),
            "@+C+B": oneshot("G"),
            # Sequence
            "@+C+A": self.clear_after(lambda: True),
            # Multi
            "D+d": self.clear_after(oneshot("D")),
            "E+e": self.clear_after(oneshot("E")),
            "F+f": self.clear_after(oneshot("F")),
            "@+F+E+D": oneshot("Z"),
            # TapHold
            # "B+!": press("X"),
            # "@+F+E+!": oneshot("Y"),
        }

    @classmethod
    def add(cls, key_name, value):
        cls._instance.updated = True
        keystrokes = cls._instance.keystrokes
        length = len(keystrokes)
        if value:
            if length == 1:
                keystrokes.insert(0, "@")
            elif length > 1 and keystrokes[0] != "@":
                keystrokes[0] = "@"
        if not value and length > 0 and keystrokes[0] == "@":
            keystrokes[0] = "_"
        if not value:
            if not keystrokes:
                key_name = str.lower(key_name)
            elif key_name in keystrokes:
                if len(keystrokes) <= 1:
                    key_name = str.lower(key_name)
                else:
                    index = keystrokes.index(key_name)
                    keystrokes.remove(key_name)
                    if len(keystrokes) == 1:
                        keystrokes.append("!")
                    print("Buffer:", "+".join(keystrokes))
                    return
        keystrokes.append(key_name)

    def clear_after(self, action):
        def func():
            action()
            self.keystrokes.clear()

        return func

    def match_to_key(self):
        if not self.keystrokes:
            return (None, None)
        content = "+".join(self.keystrokes)
        print("Buffer:", content)
        if action := self.keys.get(content, None):
            return (content, action)
        return (None, None)

    @classmethod
    def flush(cls):
        buffer = cls._instance
        if buffer.updated:
            key, action = buffer.match_to_key()
            if key:
                print("Match found: ", key)
                action()
            cls._instance.updated = False


Buffer._instance = Buffer()
