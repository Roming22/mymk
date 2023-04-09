import re
from collections import namedtuple

from seaks.hardware.keys import get_keycodes_for
from seaks.logic.action import Action
from seaks.logic.buffer import Buffer
from seaks.logic.controller import Ticker
from seaks.utils.memory import check_memory

Key = namedtuple(
    "Key",
    [
        "uid",
        "keycode",
        "patterns",
    ],
)

regex_cache: dict(str, re) = {}

press_patterns: dict[str, dict] = {1: {}}
release_patterns: dict[str, Action] = {}


@check_memory("Key")
def set(layer_uid: str, switch_uid: str, keycode: str) -> Key:
    switch_uid = f"switch.{switch_uid}"
    key_uid = f"{layer_uid}.{switch_uid}"
    print(f"\nKey: '{key_uid}'")

    try:
        if keycode == "NO" or keycode is None or get_keycodes_for(keycode):
            simple_key(key_uid, keycode)
            return
    except KeyError:
        pass
    raise RuntimeError(f"Unimplement keycode: '{keycode}'")


def simple_key(key_uid: str, keycode: str):
    switch_uid = ".".join(key_uid.split(".")[-2:])
    press_event_uid = key_uid
    release_event_uid = f"!{key_uid}"
    release_event_id = f"!{switch_uid}"

    regex_cache[press_event_uid] = re.compile(f"^(.*/)?{press_event_uid}(/.*)?$")
    regex_cache[release_event_uid] = re.compile(f"^(.*/)?{release_event_id}(/.*)?$")

    release_action = Action.chain(
        Action(lambda: release_patterns.pop(release_event_uid)),
        Action.release(keycode),
        Action.claim(release_event_id),
    )
    press_action = Action.chain(
        Action(lambda: release_patterns.update({release_event_uid: release_action})),
        Action.press(keycode),
        Action.claim(press_event_uid),
    )

    press_patterns[1][press_event_uid] = press_action


# def get(key_uid: str) -> Key:
#     try:
#         return instances[key_uid]
#     except KeyError as ex:
#         print(f"Key not found: {key_uid}")


# def simple_key_patterns(key):
#     switch_uid = ".".join(key.uid.split(".")[-2:])
#     event_pressed = key.uid
#     event_released = f"!{switch_uid}"

# def combo_patterns(key):
#     switch_uid = ".".join(key.uid.split(".")[-2:])
#     event_pressed = key.uid
#     event_released = f"!{switch_uid}"
#     patterns = dict()

#     # Oneshot
#     add_pattern(
#         patterns,
#         [event_pressed, event_released],
#         [
#             Action.oneshot(key.keycode),
#             Action.claim(event_pressed, event_released),
#         ]
#         + [Action.stop_timer(c.name) for c in key.combos],
#     )

#     for combo in key.combos:
#         print("Combo:", combo)
#         timer = combo.name

#         # Acticate combo timer
#         add_pattern(
#             patterns,
#             event_pressed,
#             Action.start_timer(timer),
#         )

#         # Combo not activated...
#         ## Press
#         add_pattern(patterns, [event_pressed, timer], Action.press(key.keycode))
#         ## Release
#         add_pattern(
#             patterns,
#             [event_pressed, timer, event_released],
#             [
#                 Action.release(key.keycode),
#                 Action.claim(event_pressed, timer, event_released),
#             ],
#         )

#         # Combo activated
#         ## Press
#         add_pattern(
#             patterns,
#             combo.key_uids,
#             [Action.oneshot(combo.keycode), Action.stop_timer(timer)],
#         )
#         # Combo activated
#         ## Release
#         # add_pattern(
#         #     patterns,
#         #     [],
#         #     [Action.release(combo.keycode)]
#         # )

#     return patterns


# def add_pattern(patterns: dict, event_ids: list, action: Action) -> None:
#     if not isinstance(event_ids, list):
#         event_ids = [event_ids]
#     regex_uid = cache_regex(*event_ids)
#     if isinstance(action, list):
#         action = Action.chain(*action)

#     complexity = len(event_ids)
#     if complexity not in patterns.keys():
#         patterns[complexity] = dict()
#     patterns[complexity][regex_uid] = action


# def cache_regex(*event_ids) -> str:
#     regex_uid = "(/.*)?/".join(event_ids)
#     regex = f"^(.*/)?{regex_uid}(/.*)?$"
#     try:
#         regex_cache[regex_uid]
#     except KeyError:
#         regex_cache[regex_uid] = re.compile(regex)
#     return regex_uid


class KeyTicker(Ticker):
    def __init__(self) -> None:
        print("Initializing keys")
        # for key in instances.values():
        #     if key.combos and key.tapholds:
        #         raise NotImplementedError("Combos and TapHolds are not implemented")
        #     elif key.combos:
        #         key.patterns.update(combo_patterns(key))
        #     elif key.tapholds:
        #         raise NotImplementedError("TapHolds are not implemented")
        #     else:
        #         key.patterns.update(simple_key_patterns(key))
        # Memory can be released
        # key.combos.clear()
        # key.tapholds.clear()
        self.register()

    def tick(self) -> None:
        for complexity in reversed(list(press_patterns.keys())):
            patterns = press_patterns[complexity]
            for regex_uid, action in patterns.items():
                if regex_cache[regex_uid].search(Buffer.instance.data):
                    action.run()
        for regex_uid, action in release_patterns.items():
            if regex_cache[regex_uid].search(Buffer.instance.data):
                action.run()
