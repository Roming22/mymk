# from typing import Callable

from seaks.hardware.keys import oneshot as key_oneshot
from seaks.hardware.keys import press as key_press
from seaks.hardware.keys import release as key_release
from seaks.logic.timer import Timer
from seaks.utils.memory import memory_cost

noop = lambda: None


@memory_cost("action.chain")
def chain(*actions) -> "Callable":
    func = lambda: [action() for action in actions]
    return func


@memory_cost("action.oneshot")
def oneshot(key_name: str) -> "Callable":
    if key_name == "NO" or key_name is None:
        return noop

    func = lambda: key_oneshot(key_name)
    return func


@memory_cost("action.press")
def press(key_name: str) -> "Callable":
    if key_name == "NO" or key_name is None:
        return noop

    func = lambda: key_press(key_name)
    return func


@memory_cost("action.release")
def release(key_name: str) -> "Callable":
    if key_name == "NO" or key_name is None:
        return noop

    func = lambda: key_release(key_name)
    return func


@memory_cost("action.start_timer")
def start_timer(timer_name: str, force=False) -> "Callable":
    func = lambda: Timer.start(timer_name)
    return func


@memory_cost("action.stop_timer")
def stop_timer(timer_name: str) -> "Callable":
    func = lambda: Timer.stop(timer_name)
    return func


@memory_cost("action.reset_timer")
def reset_timer(timer_name: str) -> "Callable":
    func = lambda: Timer.reset(timer_name)
    return func
