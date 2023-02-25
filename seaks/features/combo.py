from seaks.buffer import Buffer
from seaks.hardware.keys import oneshot, press, release


def permutations(items: list, n=None):
    if n is None:
        n = len(items)
    if n == 1:
        yield items
    else:
        for i in range(n - 1):
            for permutation in permutations(items, n - 1):
                yield permutation
            j = 0 if (n % 2) == 1 else i
            items[j], items[n - 1] = items[n - 1], items[j]
        for permutation in permutations(items, n - 1):
            yield permutation


class Sequence:
    def __init__(self, keys: list[str], key_name: str) -> None:
        key_name = str.upper(key_name)
        print(f"Sequence: {keys} = ", end="")
        # Single key
        first_key_name = keys[0]
        Buffer.unregister_event_sequence(first_key_name)
        Buffer.register_event_sequence(
            f"{first_key_name}+{str.lower(first_key_name)}",
            Buffer.clear_after(oneshot(first_key_name)),
        )
        # Combo
        command_press = "@+" + "+".join(keys)
        command_release = "_+" + "+".join(keys[:-1])
        Buffer.register_event_sequence(command_press, press(key_name))
        Buffer.register_event_sequence(command_release, release(key_name))
        print(f"{[command_press, command_release]}")


class Chord:
    def __init__(self, keys: list[str], key_name: str) -> None:
        keys = [str.upper(k) for k in keys]
        key_name = str.upper(key_name)
        for event_sequence in permutations(keys):
            Sequence(event_sequence, key_name)
