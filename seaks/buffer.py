class Buffer:
    _instance: "Buffer" = None

    @classmethod
    def instanciate(cls):
        Buffer()

    def __init__(self):
        if Buffer._instance is not None:
            raise RuntimeError("Buffer object cannot be instanciated more than once.")
        Buffer._instance = self
        self.keystrokes = []
        self.updated = False

        self.keys = {
            "_+!": self.clear_after(lambda: True),
        }

    @classmethod
    def register_event_sequence(cls, sequence, action):
        # print("Buffer.register:", sequence)
        cls._instance.keys[sequence] = action

    @classmethod
    def unregister_event_sequence(cls, sequence):
        try:
            cls._instance.keys.pop(sequence)
        except KeyError:
            pass

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
                    if len(keystrokes) == 1:
                        keystrokes.append("!")
                    print("Buffer:", "+".join(keystrokes))
                    return
        if key_name == "!":
            try:
                keystrokes.remove("!")
            except ValueError:
                pass
        keystrokes.append(key_name)

    @classmethod
    def clear_after(cls, action):
        keystrokes = cls._instance.keystrokes

        def func():
            action()
            print("Buffer: clearing keystrokes after action")
            keystrokes.clear()

        return func

    def match_to_key(self):
        if not self.keystrokes:
            return (None, None)
        content = "+".join(self.keystrokes)
        print("Buffer:", content)
        if action := self.keys.get(content, None):
            return (content, action)
        if not self.has_possible_match():
            print("Buffer: clear keystrokes")
            self.keystrokes.clear()
        return (None, None)

    def has_possible_match(self):
        content = "+".join(self.keystrokes)
        possible_matches = [k for k in self.keys.keys() if k.startswith(content)]
        return len(possible_matches) != 0

    @classmethod
    def flush(cls):
        buffer = cls._instance
        if buffer.updated:
            key, action = buffer.match_to_key()
            if key:
                print("Match found: ", key)
                action()
            cls._instance.updated = False


Buffer.instanciate()
