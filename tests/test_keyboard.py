from collections import OrderedDict
from unittest.mock import MagicMock, call

import pytest

import mymk.hardware.keys as Keys
from mymk.feature.keyboard import Keyboard
from mymk.multiverse.timeline_manager import TimelineManager
from tests.keycode import Keycode


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
