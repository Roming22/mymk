from collections import OrderedDict
from unittest.mock import MagicMock, call

import pytest

import mymk.feature.keys.taphold
import mymk.hardware.keys as Keys
from mymk.feature.keyboard import Keyboard
from mymk.multiverse.timeline_manager import TimelineManager
from tests.keycode import Keycode


def make_keyboard(definition, monkeypatch):
    kbd = MagicMock()
    action = MagicMock()
    kbd.press = lambda *args: action("press", *args)
    kbd.release = lambda *args: action("release", *args)
    monkeypatch.setattr(Keys, "_kbd", kbd)
    monkeypatch.setattr(Keys, "Keycode", Keycode)
    TimelineManager._universes.clear()
    Keyboard(definition)
    return action


def run_scenario(events):
    # Run test
    for event in events:
        TimelineManager.process_event(event)
    timeline = TimelineManager._universes[0].timeline_start
    assert timeline.events == {}
    assert timeline.children == []
    assert timeline.determined == True


class TestSingleLayerKeyboard:
    @pytest.fixture
    def action(_, monkeypatch):
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
        action = make_keyboard(definition, monkeypatch)
        return action

    @staticmethod
    def test_one_key(action):
        events = ["board.2x2.switch.0", "!board.2x2.switch.0"]
        run_scenario(events)
        assert action.call_args_list == [call("press", "A"), call("release", "A")]

    @staticmethod
    def test_two_keys_couplet(action):
        events = [
            "board.2x2.switch.0",
            "!board.2x2.switch.0",
            "board.2x2.switch.1",
            "!board.2x2.switch.1",
        ]
        run_scenario(events)
        assert action.call_args_list == [
            call("press", "A"),
            call("release", "A"),
            call("press", "B"),
            call("release", "B"),
        ]

    @staticmethod
    def test_two_keys_cross(action):
        events = [
            "board.2x2.switch.0",
            "board.2x2.switch.1",
            "!board.2x2.switch.0",
            "!board.2x2.switch.1",
        ]
        run_scenario(events)
        assert action.call_args_list == [
            call("press", "A"),
            call("press", "B"),
            call("release", "A"),
            call("release", "B"),
        ]

    @staticmethod
    def test_two_keys_enclosed(action):
        events = [
            "board.2x2.switch.0",
            "board.2x2.switch.1",
            "!board.2x2.switch.1",
            "!board.2x2.switch.0",
        ]
        run_scenario(events)
        assert action.call_args_list == [
            call("press", "A"),
            call("press", "B"),
            call("release", "B"),
            call("release", "A"),
        ]

    @staticmethod
    def test_three_keys(action):
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
        run_scenario(events)
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
    @pytest.fixture
    def action(_, monkeypatch):
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
        "TH_HD(A, F1)", "TH_TP(B, F2)",
        "TH_NO(C, F3)", "D",
                # fmt: on
            ],
        }
        action = make_keyboard(definition, monkeypatch)
        return action

    @staticmethod
    def test_tap(action):
        events = ["board.test.switch.0", "!board.test.switch.0"]
        run_scenario(events)
        assert action.call_args_list == [call("press", "A"), call("release", "A")]

    @staticmethod
    def test_hold(action):
        events = [
            "board.test.switch.0",
            "timer.board.test.switch.0.taphold",
            "!board.test.switch.0",
        ]
        run_scenario(events)
        assert action.call_args_list == [call("press", "F1"), call("release", "F1")]

    @staticmethod
    def test_interrupt_hold(action):
        events = [
            "board.test.switch.0",
            "board.test.switch.3",
            "!board.test.switch.3",
            "!board.test.switch.0",
        ]
        run_scenario(events)
        assert action.call_args_list == [
            call("press", "F1"),
            call("press", "D"),
            call("release", "D"),
            call("release", "F1"),
        ]

    @staticmethod
    def test_interrupt_noop(action):
        events = [
            "board.test.switch.2",
            "board.test.switch.3",
            "!board.test.switch.3",
            "!board.test.switch.2",
        ]
        run_scenario(events)
        assert action.call_args_list == [
            call("press", "D"),
            call("release", "D"),
        ]

    @staticmethod
    def test_interrupt_tap(action):
        events = [
            "board.test.switch.1",
            "board.test.switch.3",
            "!board.test.switch.3",
            "!board.test.switch.1",
        ]
        run_scenario(events)
        assert action.call_args_list == [
            call("press", "B"),
            call("press", "D"),
            call("release", "D"),
            call("release", "B"),
        ]

    @staticmethod
    def test_interrupt_hold_ht(action):
        events = [
            "board.test.switch.0",
            "board.test.switch.1",
            "!board.test.switch.1",
            "!board.test.switch.0",
        ]
        run_scenario(events)
        assert action.call_args_list == [
            call("press", "F1"),
            call("press", "B"),
            call("release", "B"),
            call("release", "F1"),
        ]

    @staticmethod
    def test_interrupt_noop_ht(action):
        events = [
            "board.test.switch.2",
            "board.test.switch.0",
            "!board.test.switch.0",
            "!board.test.switch.2",
        ]
        run_scenario(events)
        assert action.call_args_list == [
            call("press", "A"),
            call("release", "A"),
        ]

    @staticmethod
    def test_interrupt_tap_ht(action):
        events = [
            "board.test.switch.1",
            "board.test.switch.2",
            "!board.test.switch.2",
            "board.test.switch.2",
            "!board.test.switch.2",
            "!board.test.switch.1",
        ]
        run_scenario(events)
        assert action.call_args_list == [
            call("press", "B"),
            call("press", "C"),
            call("release", "C"),
            call("press", "C"),
            call("release", "C"),
            call("release", "B"),
        ]
