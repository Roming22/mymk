# from typing import Callable

from seaks.hardware.keys import oneshot as key_oneshot
from seaks.hardware.keys import press as key_press
from seaks.hardware.keys import release as key_release
from seaks.logic.buffer import Buffer
from seaks.logic.event import Event, Timer
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


@memory_cost("action.claim")
def claim(*event_ids) -> "Callable":
    if isinstance(event_ids, str):
        event_ids = [event_ids]

    func = lambda: [Buffer.claim(event_id) for event_id in event_ids]
    return func


@memory_cost("action.start_timer")
def start_timer(timer_name: str, force=False) -> "Callable":
    def func():
        if timer_name not in Buffer.instance.content or force:
            Timer.start(timer_name)
        return True

    return func


@memory_cost("action.stop_timer")
def stop_timer(timer_name: str) -> "Callable":
    func = lambda: Timer.stop(timer_name)
    return func


@memory_cost("action.reset_timer")
def reset_timer(timer_name: str) -> "Callable":
    func = lambda: Timer.reset(timer_name)
    return func


@memory_cost("action.trigger")
def trigger(subject: str, value: str) -> "Callable":
    Event.get(subject, value)
    func = lambda: Event.get(subject, value).fire()
    return func
