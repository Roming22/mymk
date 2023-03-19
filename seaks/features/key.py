import re
from collections import namedtuple

from seaks.logic.action import Action
from seaks.logic.buffer import Buffer
from seaks.logic.controller import Ticker
from seaks.utils.memory import check_memory

Key = namedtuple("Key", ["uid", "keycode", "combos", "tapholds", "patterns"])

instances: dict[str, Key] = {}
regex_cache: dict(str, re) = {}


@check_memory("Key")
def set(layer_uid: str, switch_uid: str, keycode=str) -> Key:
    switch_uid = f"switch.{switch_uid}"
    key_uid = f"{layer_uid}.{switch_uid}"
    patterns = dict()
    print(f"\nKey: '{key_uid}'")
    try:
        get(key_uid)
        instances.pop(key_uid)
    except KeyError:
        pass
    new_key = Key(key_uid, keycode, list(), list(), patterns)
    instances[key_uid] = new_key
    print("New key", key_uid)


def get(key_uid: str) -> Key:
    try:
        return instances[key_uid]
    except KeyError as ex:
        print(f"Key not found: {key_uid}")


def simple_key_patterns(key):
    switch_uid = ".".join(key.uid.split(".")[-2:])
    event_pressed = key.uid
    event_released = f"!{switch_uid}"

    patterns = {}
    add_pattern(
        patterns,
        event_pressed,
        [Action.press(key.keycode), Action.claim(event_pressed)],
    )
    add_pattern(
        patterns,
        event_released,
        [Action.release(key.keycode), Action.claim(event_released)],
    )
    return patterns


def combo_patterns(key):
    switch_uid = ".".join(key.uid.split(".")[-2:])
    event_pressed = key.uid
    event_released = f"!{switch_uid}"
    patterns = dict()

    # Oneshot
    add_pattern(
        patterns,
        [event_pressed, event_released],
        [
            Action.oneshot(key.keycode),
            Action.claim(event_pressed),
            Action.claim(event_released),
        ],
    )

    for combo in key.combos:
        print("Combo:", combo)

    # Combo not activated

    # Combo activated
    return patterns


def add_pattern(patterns: dict, event_ids: list, action: Action) -> None:
    if not isinstance(event_ids, list):
        event_ids = [event_ids]
    regex_uid = cache_regex(*event_ids)
    if isinstance(action, list):
        action = Action.chain(*action)
    patterns[regex_uid] = action


def cache_regex(*event_ids) -> str:
    regex_uid = "(/.*)?/".join(event_ids)
    regex = f"^(.*/)?{regex_uid}(/.*)?$"
    try:
        regex_cache[regex_uid]
    except KeyError:
        regex_cache[regex_uid] = re.compile(regex)
    return regex_uid


class KeyTicker(Ticker):
    def __init__(self) -> None:
        print("Initializing keys")
        for key in instances.values():
            if key.combos and key.tapholds:
                raise NotImplementedError("Combos and TapHolds are not implemented")
            elif key.combos:
                key.patterns.update(combo_patterns(key))
            elif key.tapholds:
                raise NotImplementedError("TapHolds are not implemented")
            else:
                key.patterns.update(simple_key_patterns(key))

        self.register()

    def tick(self) -> None:
        for uid, key in instances.items():
            patterns = key.patterns
            print(uid, "checking", patterns.keys())
            for pattern, action in patterns.items():
                if regex_cache[pattern].search(Buffer.instance.data):
                    action.run()
