# from typing import Callable

from seaks.hardware.keys import oneshot as key_oneshot
from seaks.hardware.keys import press as key_press
from seaks.hardware.keys import release as key_release
from seaks.logic.timer import Timer
from seaks.utils.memory import memory_cost

noop = lambda: None


def chain(*actions) -> "Callable":
    func = lambda: [action() for action in actions]
    return func


def oneshot(key_name: str) -> "Callable":
    if key_name == "NO" or key_name is None:
        return noop

    func = lambda: key_oneshot(key_name)
    return func


def press(key_name: str) -> "Callable":
    if key_name == "NO" or key_name is None:
        return noop

    func = lambda: key_press(key_name)
    return func


def release(key_name: str) -> "Callable":
    if key_name == "NO" or key_name is None:
        return noop

    func = lambda: key_release(key_name)
    return func


def start_timer(timer_name: str, delay: float) -> "Callable":
    func = lambda: Timer.start(timer_name, delay)
    return func


def stop_timer(timer_name: str) -> "Callable":
    func = lambda: Timer.stop(timer_name)
    return func
