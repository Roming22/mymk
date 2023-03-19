import re
from collections import namedtuple

from seaks.hardware.keys import press, release
from seaks.logic.action import Action
from seaks.logic.buffer import Buffer
from seaks.logic.controller import Controller
from seaks.utils.memory import check_memory

Key = namedtuple("Key", ["uid", "keycode", "tick"])


def start_delay(timer_name: str) -> Action:
    def func():
        Timer.start(timer_name)
        return True

    return Action(func)


instances: dict[str, Key] = {}


@check_memory("Key")
def set(layer_uid: str, switch_uid: str, keycode=str) -> Key:
    switch_uid = f"switch.{switch_uid}"
    key_uid = f"{layer_uid}.{switch_uid}"
    print(f"\nKey: '{key_uid}'")
    pressed = re.compile(f"^(.*/)?{key_uid}(/.*)?")
    released = re.compile(f"^(.*/)?!{switch_uid}(/.*)?")

    def tick() -> None:
        print(
            key_uid,
            "checking",
            f"^(.*/)?{key_uid}(/.*)?",
            "and",
            f"^(.*/)?!{switch_uid}(/.*)?",
        )
        if pressed.search(Buffer.instance.data):
            Buffer.claim(key_uid)
            press(keycode)
        elif released.search(Buffer.instance.data):
            Buffer.claim(f"!{switch_uid}")
            release(keycode)

    try:
        get(key_uid)
        instances.pop(key_uid)
    except KeyError:
        pass
    new_key = Key(key_uid, keycode, tick)
    instances[key_uid] = new_key
    Controller.register(new_key)
    print("New key", key_uid)


def get(key_uid: str) -> Key:
    try:
        return instances[key_uid]
    except KeyError as ex:
        # print(f"Keys: {instances.keys()}")
        print(f"Key not found: {key_uid}")
