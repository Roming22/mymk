from seaks.hardware.keys import panic


class Buffer:
    _instance: "Buffer" = None

    @classmethod
    def instanciate(cls):
        Buffer()

    def __init__(self):
        if Buffer._instance is not None:
            raise RuntimeError("Buffer object cannot be instanciated more than once.")
        Buffer._instance = self
        self.commands = []
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
    def add(cls, command):
        commands = cls._instance.commands
        commands_count = len(commands)

        if str.isalpha(command):
            if command == str.upper(command):
                cls.add_key_press(command)
            else:
                cls.add_key_release(command)
        if command.startswith("*"):
            cls.add_timeout(command)
        cls._instance.updated = len(commands) != commands_count
        print(f"Buffer: {cls._instance}")

    @classmethod
    def add_key_press(cls, key_name: str) -> None:
        print(f"    Buffer: Pressing '{key_name}'")
        commands = cls._instance.commands
        cmd_count = len(commands)
        if len(commands) == 1:
            commands.insert(0, "@")
        elif cmd_count > 1 and commands[0] != "@":
            commands[0] = "@"
        commands.append(key_name)

    @classmethod
    def add_key_release(cls, command: str) -> None:
        print(f"    Buffer: Releasing '{str.upper(command)}'")
        commands = cls._instance.commands
        cmd_count = len(commands)
        if cmd_count == 0:
            commands.append(command)
            return

        if str.upper(command) not in commands:
            # Panic?
            panic()
            return

        if commands[0] == "@":
            commands[0] = "_"
        commands.append(command)

    @classmethod
    def add_timeout(cls, command: str) -> None:
        buffer = cls._instance
        key = command[1]
        commands = buffer.commands
        if len(commands) > 0 and commands[-1] == key:
            commands.append(command)
            if buffer.has_possible_match():
                print(f"    Buffer: Adding timeout")
            else:
                # Ignore timeout if does not concern the latest key pressed
                commands = commands[:-1]
        # else:
        #     print(f"    Buffer: Ignore timeout for {key}")
        #     print(f"        key: {key}, commands: {commands}")

    @classmethod
    def clear_after(cls, action):
        commands = cls._instance.commands

        def func():
            action()
            print("    Buffer: clearing commands after action")
            Buffer.clear_commands()

        return func

    def __repr__(self) -> str:
        return "+".join(self.commands)

    def match_to_key(self):
        if not self.commands:
            return (None, None)
        content = f"{self}"
        if action := self.keys.get(content, None):
            return (content, action)
        if not self.has_possible_match():
            Buffer.clear_commands()
        return (None, None)

    def has_possible_match(self):
        content = f"{self}"
        possible_matches = [k for k in self.keys.keys() if k.startswith(content)]
        return len(possible_matches) != 0

    @classmethod
    def clear_commands(cls):
        print("    Buffer: clear commands\n\n\n")
        cls._instance.commands.clear()

    @classmethod
    def flush(cls):
        buffer = cls._instance
        if buffer.updated:
            key, action = buffer.match_to_key()
            if key:
                print("    Match found: ", key)
                action()
            cls._instance.updated = False


Buffer.instanciate()
