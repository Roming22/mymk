import re
from collections import namedtuple

from seaks.logic.action import Action
from seaks.logic.buffer import Buffer
from seaks.logic.controller import Ticker
from seaks.utils.memory import check_memory

Key = namedtuple("Key", ["uid", "keycode", "combos", "tapholds", "patterns"])


def start_delay(timer_name: str) -> Action:
    def func():
        Timer.start(timer_name)
        return True

    return Action(func)


instances: dict[str, Key] = {}
regex_cache: dict(str, re) = {}


@check_memory("Key")
def set(layer_uid: str, switch_uid: str, keycode=str) -> Key:
    switch_uid = f"switch.{switch_uid}"
    key_uid = f"{layer_uid}.{switch_uid}"
    patterns = dict()
    print(f"\nKey: '{key_uid}'")
    pressed = re.compile(f"^(.*/)?{key_uid}(/.*)?")
    released = re.compile(f"^(.*/)?!{switch_uid}(/.*)?")

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

    cache_regex(event_pressed)
    cache_regex(event_released)

    patterns = {}
    patterns[event_pressed] = Action.chain(
        Action.press(key.keycode), Action.claim(event_pressed)
    )
    patterns[event_released] = Action.chain(
        Action.release(key.keycode), Action.claim(event_released)
    )
    return patterns


def cache_regex(event_id):
    regex = f"^(.*/)?{event_id}(/.*)?"
    try:
        regex_cache[event_id]
    except KeyError:
        regex_cache[event_id] = re.compile(regex)


class KeyTicker(Ticker):
    def __init__(self) -> None:
        print("Initializing keys")
        for key in instances.values():
            if not key.combos and not key.tapholds:
                key.patterns.update(simple_key_patterns(key))
            else:
                raise NotImplemented("Combos and TapHolds are not implemented")
        self.register()

    def tick(self) -> None:
        for uid, key in instances.items():
            patterns = key.patterns
            print(uid, "checking", patterns.keys())
            for pattern, action in patterns.items():
                if regex_cache[pattern].search(Buffer.instance.data):
                    action.run()
