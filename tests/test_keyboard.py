from collections import OrderedDict
from random import shuffle
from time import sleep
from unittest.mock import MagicMock, call

import pytest

import mymk.feature.keys.taphold
import mymk.hardware.keys as Keys
from mymk.feature.keyboard import Keyboard
from mymk.hardware.board import Board
from mymk.logic.timer import Timer
from mymk.multiverse.timeline_manager import TimelineManager
from tests.keycode import Keycode


def make_keyboard(definition, monkeypatch):
    kbd = MagicMock()
    action = MagicMock()
    kbd.press = lambda *args: action("press", *args)
    kbd.release = lambda *args: action("release", *args)
    monkeypatch.setattr(Keys, "_kbd", kbd)
    monkeypatch.setattr(Keys, "Keycode", Keycode)
    Board._instances.clear()
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


class TestSingleLayerKeyboard:
    @staticmethod
    def _setup(monkeypatch, events):
        # Hardware definition
        definition = {
            "hardware": {
                "2x2": {
                    "pins": {
                        "cols": (1, 2),
                        "rows": (1, 2),
                    },
                },
            },
            "layout": {"layers": OrderedDict()},
        }

        # Layer definition
        definition["layout"]["layers"]["myLayer"] = {
            "keys": [
                # fmt: off
                "A", "B",
                "C", "D",
                # fmt: on
            ],
        }
        keyboard, action = make_keyboard(definition, monkeypatch)
        keyboard.boards[0].get_event = MagicMock(side_effect=events)
        event_delays = [0] * len(events)
        return keyboard, event_delays, action

    @classmethod
    def test_one_key(cls, monkeypatch):
        events = ["board.2x2.switch.0", "!board.2x2.switch.0"]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [call("press", "A"), call("release", "A")]

    @classmethod
    def test_two_keys_couplet(cls, monkeypatch):
        events = [
            "board.2x2.switch.0",
            "!board.2x2.switch.0",
            "board.2x2.switch.1",
            "!board.2x2.switch.1",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "A"),
            call("release", "A"),
            call("press", "B"),
            call("release", "B"),
        ]

    @classmethod
    def test_two_keys_cross(cls, monkeypatch):
        events = [
            "board.2x2.switch.0",
            "board.2x2.switch.1",
            "!board.2x2.switch.0",
            "!board.2x2.switch.1",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "A"),
            call("press", "B"),
            call("release", "A"),
            call("release", "B"),
        ]

    @classmethod
    def test_two_keys_enclosed(cls, monkeypatch):
        events = [
            "board.2x2.switch.0",
            "board.2x2.switch.1",
            "!board.2x2.switch.1",
            "!board.2x2.switch.0",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "A"),
            call("press", "B"),
            call("release", "B"),
            call("release", "A"),
        ]

    @classmethod
    def test_three_keys(cls, monkeypatch):
        events = [
            "board.2x2.switch.0",
            "board.2x2.switch.1",
            "!board.2x2.switch.1",
            "board.2x2.switch.2",
            "!board.2x2.switch.0",
            "board.2x2.switch.0",
            "!board.2x2.switch.0",
            "!board.2x2.switch.2",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "A"),
            call("press", "B"),
            call("release", "B"),
            call("press", "C"),
            call("release", "A"),
            call("press", "A"),
            call("release", "A"),
            call("release", "C"),
        ]


class TestTapHold:
    @staticmethod
    def _setup(monkeypatch, events):
        # Hardware definition
        definition = {
            "hardware": {
                "test": {
                    "pins": {
                        "cols": (1, 2),
                        "rows": (1, 2),
                    },
                },
            },
            "layout": {"layers": OrderedDict()},
        }

        # Layer definition
        definition["layout"]["layers"]["myLayer"] = {
            "keys": [
                # fmt: off
        "TH_HD(A, 0.1, F1)", "TH_TP(B, 0.1, F2)",
        "TH_NO(C, 0.1, F3)", "D",
                # fmt: on
            ],
        }
        keyboard, action = make_keyboard(definition, monkeypatch)
        keyboard.boards[0].get_event = MagicMock(side_effect=events)
        event_delays = [0] * len(events)
        return keyboard, event_delays, action

    @classmethod
    def test_tap(cls, monkeypatch):
        events = ["board.test.switch.0", "!board.test.switch.0"]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [call("press", "A"), call("release", "A")]

    @classmethod
    def test_hold(cls, monkeypatch):
        events = [
            "board.test.switch.0",
            "!board.test.switch.0",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        event_delays[1] = 0.2
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [call("press", "F1"), call("release", "F1")]

    @classmethod
    def test_interrupt_hold(cls, monkeypatch):
        events = [
            "board.test.switch.0",
            "board.test.switch.3",
            "!board.test.switch.3",
            "!board.test.switch.0",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "F1"),
            call("press", "D"),
            call("release", "D"),
            call("release", "F1"),
        ]

    @classmethod
    def test_interrupt_noop(cls, monkeypatch):
        events = [
            "board.test.switch.2",
            "board.test.switch.3",
            "!board.test.switch.3",
            "!board.test.switch.2",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "D"),
            call("release", "D"),
        ]

    @classmethod
    def test_interrupt_tap(cls, monkeypatch):
        events = [
            "board.test.switch.1",
            "board.test.switch.3",
            "!board.test.switch.3",
            "!board.test.switch.1",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "B"),
            call("press", "D"),
            call("release", "D"),
            call("release", "B"),
        ]

    @classmethod
    def test_interrupt_hold_ht(cls, monkeypatch):
        events = [
            "board.test.switch.0",
            "board.test.switch.1",
            "!board.test.switch.1",
            "!board.test.switch.0",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "F1"),
            call("press", "B"),
            call("release", "B"),
            call("release", "F1"),
        ]

    @classmethod
    def test_interrupt_noop_ht(cls, monkeypatch):
        events = [
            "board.test.switch.2",
            "board.test.switch.0",
            "!board.test.switch.0",
            "!board.test.switch.2",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "A"),
            call("release", "A"),
        ]

    @classmethod
    def test_interrupt_tap_ht(cls, monkeypatch):
        events = [
            "board.test.switch.1",
            "board.test.switch.2",
            "!board.test.switch.2",
            "board.test.switch.2",
            "!board.test.switch.2",
            "!board.test.switch.1",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "B"),
            call("press", "C"),
            call("release", "C"),
            call("press", "C"),
            call("release", "C"),
            call("release", "B"),
        ]


class TestCombo:
    @staticmethod
    def _setup(monkeypatch, events):
        # Hardware definition
        definition = {
            "hardware": {
                "test": {
                    "pins": {
                        "cols": (1, 2),
                        "rows": (1, 2, 3),
                    },
                },
            },
            "layout": {"layers": OrderedDict()},
        }

        # Layer definition
        definition["layout"]["layers"]["myLayer"] = {
            "keys": [
                # fmt: off
                "A", "B",
                "C", "D",
                "E", "F",
                # fmt: on
            ],
            "combos": {
                "chords": {
                    "4*5": "F4",
                },
                "sequences": {
                    "0+1": "F1",
                    "1+2": "F2",
                    "1+2+3": "F3",
                },
            },
        }
        keyboard, action = make_keyboard(definition, monkeypatch)
        keyboard.boards[0].get_event = MagicMock(side_effect=events)
        event_delays = [0] * len(events)
        return keyboard, event_delays, action

    @classmethod
    def test_no_combo(cls, monkeypatch):
        events = [
            "board.test.switch.0",
            "!board.test.switch.0",
            "board.test.switch.1",
            "!board.test.switch.1",
            "board.test.switch.1",
            "board.test.switch.0",
            "!board.test.switch.0",
            "!board.test.switch.1",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        event_delays[5] = 1.1
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "A"),
            call("release", "A"),
            call("press", "B"),
            call("release", "B"),
            call("press", "B"),
            call("press", "A"),
            call("release", "A"),
            call("release", "B"),
        ]

    @classmethod
    def test_chord(cls, monkeypatch):
        events = [
            "board.test.switch.5",
            "board.test.switch.4",
            "!board.test.switch.5",
            "!board.test.switch.4",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "F4"),
            call("release", "F4"),
        ]

    @classmethod
    def test_2key_enclosed(cls, monkeypatch):
        events = [
            "board.test.switch.0",
            "board.test.switch.1",
            "!board.test.switch.1",
            "!board.test.switch.0",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [call("press", "F1"), call("release", "F1")]

    @classmethod
    def test_2key_cross(cls, monkeypatch):
        events = [
            "board.test.switch.0",
            "board.test.switch.1",
            "!board.test.switch.0",
            "!board.test.switch.1",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [call("press", "F1"), call("release", "F1")]

    @classmethod
    def test_3key(cls, monkeypatch):
        events = [
            "board.test.switch.1",
            "board.test.switch.2",
            "board.test.switch.3",
        ]
        release_events = [
            "!board.test.switch.1",
            "!board.test.switch.2",
            "!board.test.switch.3",
        ]
        shuffle(release_events)
        events += release_events
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [call("press", "F3"), call("release", "F3")]

    @classmethod
    def test_sequence_break(cls, monkeypatch):
        events = [
            "board.test.switch.1",
            "board.test.switch.2",
            "board.test.switch.0",
            "!board.test.switch.0",
            "board.test.switch.3",
            "!board.test.switch.1",
            "!board.test.switch.3",
            "!board.test.switch.2",
            "board.test.switch.2",
            "!board.test.switch.2",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "F2"),
            call("press", "A"),
            call("release", "A"),
            call("press", "D"),
            call("release", "F2"),
            call("release", "D"),
            call("press", "C"),
            call("release", "C"),
        ]


class TestTapHoldCombo:
    @staticmethod
    def _setup(monkeypatch, events):
        # Hardware definition
        definition = {
            "hardware": {
                "test": {
                    "pins": {
                        "cols": (1, 2),
                        "rows": (1, 2),
                    },
                },
            },
            "layout": {"layers": OrderedDict()},
        }

        # Layer definition
        definition["layout"]["layers"]["myLayer"] = {
            "keys": [
                # fmt: off
        "TH_HD(A, ONE)",    "TH_TP(B, TWO)",
        "C",                "D",
                # fmt: on
            ],
            "combos": {
                "sequences": {
                    "0+1": "F1",
                    "1+2": "F2",
                    "1+2+3": "F3",
                },
            },
        }
        keyboard, action = make_keyboard(definition, monkeypatch)
        keyboard.boards[0].get_event = MagicMock(side_effect=events)
        event_delays = [0] * len(events)
        return keyboard, event_delays, action

    @classmethod
    def test_tap(cls, monkeypatch):
        events = [
            "board.test.switch.0",
            "!board.test.switch.0",
            "board.test.switch.2",
            "!board.test.switch.2",
            "board.test.switch.1",
            "!board.test.switch.1",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "A"),
            call("release", "A"),
            call("press", "C"),
            call("release", "C"),
            call("press", "B"),
            call("release", "B"),
        ]

    @classmethod
    def test_hold(cls, monkeypatch):
        events = [
            "board.test.switch.0",
            "!board.test.switch.0",
            "board.test.switch.2",
            "!board.test.switch.2",
            "board.test.switch.1",
            "!board.test.switch.1",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        event_delays[1] = .4
        event_delays[5] = .4
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "ONE"),
            call("release", "ONE"),
            call("press", "C"),
            call("release", "C"),
            call("press", "TWO"),
            call("release", "TWO"),
        ]

    @classmethod
    def test_combo(cls, monkeypatch):
        events = [
            "board.test.switch.0",
            "board.test.switch.1",
            "!board.test.switch.0",
            "!board.test.switch.1",
            "board.test.switch.3",
            "!board.test.switch.3",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "F1"),
            call("release", "F1"),
            call("press", "D"),
            call("release", "D"),
        ]
