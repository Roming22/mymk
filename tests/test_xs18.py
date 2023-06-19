from time import sleep
from unittest.mock import MagicMock, call

import mymk.hardware.keys
from layouts.xs18 import get_definition
from mymk.feature.keyboard import Keyboard
from mymk.logic.timer import Timer
from mymk.multiverse.timeline_manager import TimelineManager


def make_keyboard(definition, monkeypatch):
    action = MagicMock()
    press = lambda *args: action("press", *args)
    release = lambda *args: action("release", *args)
    monkeypatch.setattr(mymk.hardware.keys._kbd, "press", press)
    monkeypatch.setattr(mymk.hardware.keys._kbd, "release", release)

    TimelineManager._universes.clear()
    Timer.running.clear()
    keyboard = Keyboard(definition)
    return keyboard, action


def run_scenario(keyboard, event_delays):
    # Run test
    for event_delay in event_delays:
        sleep(event_delay)
        keyboard.tick()
    timeline = TimelineManager._universes[0].timeline_start
    assert timeline.events == {}
    assert timeline.children == []
    assert timeline.determined == True


class TestKeyboard:
    @staticmethod
    def _setup(monkeypatch, events):
        # Hardware definition
        definition = get_definition()
        keyboard, action = make_keyboard(definition, monkeypatch)
        keyboard.board.get_event_controller = MagicMock(side_effect=events)
        event_delays = [0] * len(events)
        return keyboard, event_delays, action

    @classmethod
    def test_one_key(cls, monkeypatch):
        events = ["board.KEYBOARD-L.switch.5", "!board.KEYBOARD-L.switch.5"]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [call("press", "T"), call("release", "T")]

    @classmethod
    def test_one_key_hold(cls, monkeypatch):
        events = ["board.KEYBOARD-L.switch.1", "!board.KEYBOARD-L.switch.1"]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        event_delays[1] = 0.4
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "LEFT_SHIFT"),
            call("release", "LEFT_SHIFT"),
        ]

    @classmethod
    def test_2key_combo(cls, monkeypatch):
        events = [
            "board.KEYBOARD-L.switch.5",
            "board.KEYBOARD-L.switch.6",
            "!board.KEYBOARD-L.switch.6",
            "!board.KEYBOARD-L.switch.5",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [call("press", "F"), call("release", "F")]

    @classmethod
    def test_3key_combo(cls, monkeypatch):
        events = [
            "board.KEYBOARD-L.switch.1",
            "board.KEYBOARD-L.switch.2",
            "board.KEYBOARD-L.switch.3",
            "!board.KEYBOARD-L.switch.1",
            "!board.KEYBOARD-L.switch.2",
            "!board.KEYBOARD-L.switch.3",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "ESCAPE"),
            call("release", "ESCAPE"),
        ]
