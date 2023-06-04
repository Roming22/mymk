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


class TestKeyboard:
    @pytest.fixture
    def action(_, monkeypatch):
        # Hardware definition
        definition = {
            "hardware": {
                "xs18": {
                    "pins": {
                        "cols": (1, 2, 3, 4),
                        "rows": (1, 2, 3),
                    },
                    "split": True,
                },
            },
            "layout": {"layers": OrderedDict()},
        }

        # Layer definition
        definition["layout"]["layers"]["myLayer"] = {
            "keys": [
                # fmt: off
        "TH_HD(ESC,LSFT)",  "TH_HD(D, LSFT)",   "TH_HD(C,LALT)",    "TH_HD(L,LCTL)",
        "NO",               "T",                "A",                "E",
                            "NO",               "SPACE",            "LGUI",         "NO",

                "TH_HD(R,RCTL)",    "TH_HD(S,RALT)",    "TH_HD(H,RSFT)",    "TH_HD(ENTER,RSFT)",
                "I",                "O",                "N",                "NO",
        "NO",   "RGUI",             "MEH",              "NO",
                # fmt: on
            ],
            "combos": {
                "1+2": "X",
                "2+1": "X",
                "2+3": "V",
                "3+2": "V",
                "1+3": "Z",
                "3+1": "Z",
                "5+6": "F",
                "6+5": "F",
                "6+7": "U",
                "7+6": "U",
                "5+7": "P",
                "7+5": "P",
                "5+6+7": "W",
                "12+13": "K",
                "13+12": "K",
                "13+14": "Q",
                "14+13": "Q",
                "12+14": "J",
                "14+12": "J",
                "16+17": "Y",
                "17+16": "Y",
                "17+18": "G",
                "18+17": "G",
                "16+18": "M",
                "18+16": "M",
                "18+17+16": "B",
            },
        }
        action = make_keyboard(definition, monkeypatch)
        return action

    @staticmethod
    def test_one_key(action):
        events = ["board.xs18.switch.5", "!board.xs18.switch.5"]
        run_scenario(events)
        assert action.call_args_list == [call("press", "T"), call("release", "T")]

    @staticmethod
    def test_2key_combo(action):
        events = [
            "board.xs18.switch.5",
            "board.xs18.switch.6",
            "!board.xs18.switch.6",
            "!board.xs18.switch.5",
            "board.xs18.switch.5",
            "!board.xs18.switch.5",
        ]
        run_scenario(events)
        assert action.call_args_list == [
            call("press", "F"),
            call("release", "F"),
            call("press", "T"),
            call("release", "T"),
        ]

    @staticmethod
    def test_3key_combo(action):
        events = [
            "board.xs18.switch.5",
            "board.xs18.switch.6",
            "board.xs18.switch.7",
            "!board.xs18.switch.5",
            "!board.xs18.switch.6",
            "!board.xs18.switch.7",
            "board.xs18.switch.5",
            "!board.xs18.switch.5",
        ]
        run_scenario(events)
        assert action.call_args_list == [
            call("press", "W"),
            call("release", "W"),
            call("press", "T"),
            call("release", "T"),
        ]
