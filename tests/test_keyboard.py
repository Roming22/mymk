from random import shuffle
from time import sleep
from unittest.mock import MagicMock, call

import mymk.hardware.keys
from mymk.feature.keyboard import Keyboard
from mymk.hardware.board import Board
from mymk.logic.timer import Timer
from mymk.multiverse.timeline_manager import TimelineManager
from mymk.utils.time import Time


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

    # Increasing the precision should not be necessary until tests need to be more
    # precise than a 10th of a second
    precision = 10

    for event_delay in event_delays:
        # In order to test nested TapHolds, time must flow in small chunks
        for _ in range(0, int(event_delay * precision)):
            sleep(1 / precision)
            Time.tick()
            Timer.tick()
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
                "KEYBOARD-L": {
                    "pins": {
                        "cols": (1, 2),
                        "rows": (1, 2),
                    },
                },
            },
            "layout": {
                "layers": {
                    "myLayer": {
                        "keys": [
                            # fmt: off
                            "A", "B",
                            "C", "D",
                            # fmt: on
                        ],
                    },
                },
            },
            "settings": {
                "default_layer": "myLayer",
            },
        }
        keyboard, action = make_keyboard(definition, monkeypatch)
        keyboard.board.get_event_controller = MagicMock(side_effect=events)
        event_delays = [0] * len(events)
        return keyboard, event_delays, action

    @classmethod
    def test_one_key(cls, monkeypatch):
        events = ["board.KEYBOARD-L.switch.0", "!board.KEYBOARD-L.switch.0"]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [call("press", "A"), call("release", "A")]

    @classmethod
    def test_two_keys_couplet(cls, monkeypatch):
        events = [
            "board.KEYBOARD-L.switch.0",
            "!board.KEYBOARD-L.switch.0",
            "board.KEYBOARD-L.switch.1",
            "!board.KEYBOARD-L.switch.1",
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
            "board.KEYBOARD-L.switch.0",
            "board.KEYBOARD-L.switch.1",
            "!board.KEYBOARD-L.switch.0",
            "!board.KEYBOARD-L.switch.1",
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
            "board.KEYBOARD-L.switch.0",
            "board.KEYBOARD-L.switch.1",
            "!board.KEYBOARD-L.switch.1",
            "!board.KEYBOARD-L.switch.0",
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
            "board.KEYBOARD-L.switch.0",
            "board.KEYBOARD-L.switch.1",
            "!board.KEYBOARD-L.switch.1",
            "board.KEYBOARD-L.switch.2",
            "!board.KEYBOARD-L.switch.0",
            "board.KEYBOARD-L.switch.0",
            "!board.KEYBOARD-L.switch.0",
            "!board.KEYBOARD-L.switch.2",
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
                "KEYBOARD-L": {
                    "pins": {
                        "cols": (1, 2),
                        "rows": (1, 2),
                    },
                },
            },
            "layout": {
                "layers": {
                    "myLayer": {
                        "keys": [
                            # fmt: off
            "TH_HD(A, 0.1, F1)", "TH_TP(B, 0.1, F2)",
            "TH_NO(C, 0.1, F3)", "D",
                            # fmt: on
                        ],
                    },
                }
            },
            "settings": {
                "default_layer": "myLayer",
            },
        }

        # Layer definition
        keyboard, action = make_keyboard(definition, monkeypatch)
        keyboard.board.get_event_controller = MagicMock(side_effect=events)
        event_delays = [0] * len(events)
        return keyboard, event_delays, action

    @classmethod
    def test_tap(cls, monkeypatch):
        events = ["board.KEYBOARD-L.switch.0", "!board.KEYBOARD-L.switch.0"]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [call("press", "A"), call("release", "A")]

    @classmethod
    def test_hold(cls, monkeypatch):
        events = [
            "board.KEYBOARD-L.switch.0",
            "!board.KEYBOARD-L.switch.0",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        event_delays[1] = 0.2
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [call("press", "F1"), call("release", "F1")]

    @classmethod
    def test_interrupt_hold(cls, monkeypatch):
        events = [
            "board.KEYBOARD-L.switch.0",
            "board.KEYBOARD-L.switch.3",
            "!board.KEYBOARD-L.switch.3",
            "!board.KEYBOARD-L.switch.0",
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
            "board.KEYBOARD-L.switch.2",
            "board.KEYBOARD-L.switch.3",
            "!board.KEYBOARD-L.switch.3",
            "!board.KEYBOARD-L.switch.2",
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
            "board.KEYBOARD-L.switch.1",
            "board.KEYBOARD-L.switch.3",
            "!board.KEYBOARD-L.switch.3",
            "!board.KEYBOARD-L.switch.1",
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
            "board.KEYBOARD-L.switch.0",
            "board.KEYBOARD-L.switch.1",
            "!board.KEYBOARD-L.switch.1",
            "!board.KEYBOARD-L.switch.0",
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
            "board.KEYBOARD-L.switch.2",
            "board.KEYBOARD-L.switch.0",
            "!board.KEYBOARD-L.switch.0",
            "!board.KEYBOARD-L.switch.2",
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
            "board.KEYBOARD-L.switch.1",
            "board.KEYBOARD-L.switch.2",
            "!board.KEYBOARD-L.switch.2",
            "board.KEYBOARD-L.switch.2",
            "!board.KEYBOARD-L.switch.2",
            "!board.KEYBOARD-L.switch.1",
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
                "KEYBOARD-L": {
                    "pins": {
                        "cols": (1, 2),
                        "rows": (1, 2, 3),
                    },
                },
            },
            "layout": {
                "layers": {
                    "myLayer": {
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
                    },
                },
            },
            "settings": {
                "default_layer": "myLayer",
            },
        }

        # Layer definition
        keyboard, action = make_keyboard(definition, monkeypatch)
        keyboard.board.get_event_controller = MagicMock(side_effect=events)
        event_delays = [0] * len(events)
        return keyboard, event_delays, action

    @classmethod
    def test_no_combo(cls, monkeypatch):
        events = [
            "board.KEYBOARD-L.switch.0",
            "!board.KEYBOARD-L.switch.0",
            "board.KEYBOARD-L.switch.1",
            "!board.KEYBOARD-L.switch.1",
            "board.KEYBOARD-L.switch.1",
            "board.KEYBOARD-L.switch.0",
            "!board.KEYBOARD-L.switch.0",
            "!board.KEYBOARD-L.switch.1",
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
            "board.KEYBOARD-L.switch.5",
            "board.KEYBOARD-L.switch.4",
            "!board.KEYBOARD-L.switch.5",
            "!board.KEYBOARD-L.switch.4",
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
            "board.KEYBOARD-L.switch.0",
            "board.KEYBOARD-L.switch.1",
            "!board.KEYBOARD-L.switch.1",
            "!board.KEYBOARD-L.switch.0",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [call("press", "F1"), call("release", "F1")]

    @classmethod
    def test_2key_cross(cls, monkeypatch):
        events = [
            "board.KEYBOARD-L.switch.0",
            "board.KEYBOARD-L.switch.1",
            "!board.KEYBOARD-L.switch.0",
            "!board.KEYBOARD-L.switch.1",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [call("press", "F1"), call("release", "F1")]

    @classmethod
    def test_3key(cls, monkeypatch):
        events = [
            "board.KEYBOARD-L.switch.1",
            "board.KEYBOARD-L.switch.2",
            "board.KEYBOARD-L.switch.3",
        ]
        release_events = [
            "!board.KEYBOARD-L.switch.1",
            "!board.KEYBOARD-L.switch.2",
            "!board.KEYBOARD-L.switch.3",
        ]
        shuffle(release_events)
        events += release_events
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [call("press", "F3"), call("release", "F3")]

    @classmethod
    def test_sequence_break(cls, monkeypatch):
        events = [
            "board.KEYBOARD-L.switch.1",
            "board.KEYBOARD-L.switch.2",
            "board.KEYBOARD-L.switch.0",
            "!board.KEYBOARD-L.switch.0",
            "board.KEYBOARD-L.switch.3",
            "!board.KEYBOARD-L.switch.1",
            "!board.KEYBOARD-L.switch.3",
            "!board.KEYBOARD-L.switch.2",
            "board.KEYBOARD-L.switch.2",
            "!board.KEYBOARD-L.switch.2",
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
                "KEYBOARD-L": {
                    "pins": {
                        "cols": (1, 2),
                        "rows": (1, 2),
                    },
                },
            },
            "layout": {
                "layers": {
                    "myLayer": {
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
                }
            },
            "settings": {
                "default_layer": "myLayer",
            },
        }

        keyboard, action = make_keyboard(definition, monkeypatch)
        keyboard.board.get_event_controller = MagicMock(side_effect=events)
        event_delays = [0] * len(events)
        return keyboard, event_delays, action

    @classmethod
    def test_tap(cls, monkeypatch):
        events = [
            "board.KEYBOARD-L.switch.0",
            "!board.KEYBOARD-L.switch.0",
            "board.KEYBOARD-L.switch.2",
            "!board.KEYBOARD-L.switch.2",
            "board.KEYBOARD-L.switch.1",
            "!board.KEYBOARD-L.switch.1",
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
            "board.KEYBOARD-L.switch.0",
            "!board.KEYBOARD-L.switch.0",
            "board.KEYBOARD-L.switch.2",
            "!board.KEYBOARD-L.switch.2",
            "board.KEYBOARD-L.switch.1",
            "!board.KEYBOARD-L.switch.1",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        event_delays[1] = 0.4
        event_delays[5] = 0.4
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
            "board.KEYBOARD-L.switch.0",
            "board.KEYBOARD-L.switch.1",
            "!board.KEYBOARD-L.switch.0",
            "!board.KEYBOARD-L.switch.1",
            "board.KEYBOARD-L.switch.3",
            "!board.KEYBOARD-L.switch.3",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "F1"),
            call("release", "F1"),
            call("press", "D"),
            call("release", "D"),
        ]


class TestLayer:
    @staticmethod
    def _setup(monkeypatch, events):
        # Hardware definition
        definition = {
            "hardware": {
                "KEYBOARD-L": {
                    "pins": {
                        "cols": (1, 2),
                        "rows": (1, 2),
                    },
                },
            },
            "layout": {
                "layers": {
                    "default": {
                        "keys": [
                            # fmt: off
            "A",        "B",
            "LY_MO(1)", "LY_TO(1)",
                            # fmt: on
                        ],
                    },
                    "1": {
                        "keys": [
                            # fmt: off
            "C",                "D",
            "LY_TO(default)",   "LY_MO(2)",
                            # fmt: on
                        ],
                    },
                    "2": {
                        "keys": [
                            # fmt: off
            "E", "F",
            "G", "H",
                            # fmt: on
                        ],
                    },
                }
            },
            "settings": {
                "default_layer": "default",
            },
        }

        keyboard, action = make_keyboard(definition, monkeypatch)
        keyboard.board.get_event_controller = MagicMock(side_effect=events)
        event_delays = [0] * len(events)
        return keyboard, event_delays, action

    @classmethod
    def test_ly_mo_enclosed(cls, monkeypatch):
        events = [
            "board.KEYBOARD-L.switch.2",
            "board.KEYBOARD-L.switch.0",
            "!board.KEYBOARD-L.switch.0",
            "!board.KEYBOARD-L.switch.2",
            "board.KEYBOARD-L.switch.0",
            "!board.KEYBOARD-L.switch.0",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "C"),
            call("release", "C"),
            call("press", "A"),
            call("release", "A"),
        ]

    @classmethod
    def test_ly_mo_cross(cls, monkeypatch):
        events = [
            "board.KEYBOARD-L.switch.2",
            "board.KEYBOARD-L.switch.0",
            "!board.KEYBOARD-L.switch.2",
            "!board.KEYBOARD-L.switch.0",
            "board.KEYBOARD-L.switch.0",
            "!board.KEYBOARD-L.switch.0",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "C"),
            call("release", "C"),
            call("press", "A"),
            call("release", "A"),
        ]

    @classmethod
    def test_ly_to_enclosed(cls, monkeypatch):
        events = [
            "board.KEYBOARD-L.switch.3",
            "!board.KEYBOARD-L.switch.3",
            "board.KEYBOARD-L.switch.0",
            "!board.KEYBOARD-L.switch.0",
            "board.KEYBOARD-L.switch.2",
            "!board.KEYBOARD-L.switch.2",
            "board.KEYBOARD-L.switch.0",
            "!board.KEYBOARD-L.switch.0",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "C"),
            call("release", "C"),
            call("press", "A"),
            call("release", "A"),
        ]

    @classmethod
    def test_ly_to_cross(cls, monkeypatch):
        events = [
            "board.KEYBOARD-L.switch.3",
            "board.KEYBOARD-L.switch.0",
            "!board.KEYBOARD-L.switch.3",
            "!board.KEYBOARD-L.switch.0",
            "board.KEYBOARD-L.switch.2",
            "board.KEYBOARD-L.switch.0",
            "!board.KEYBOARD-L.switch.2",
            "!board.KEYBOARD-L.switch.0",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "C"),
            call("release", "C"),
            call("press", "A"),
            call("release", "A"),
        ]

    @classmethod
    def test_ly_multiple(cls, monkeypatch):
        events = [
            "board.KEYBOARD-L.switch.2",
            "board.KEYBOARD-L.switch.0",
            "!board.KEYBOARD-L.switch.0",
            "board.KEYBOARD-L.switch.3",
            "!board.KEYBOARD-L.switch.2",
            "board.KEYBOARD-L.switch.0",
            "!board.KEYBOARD-L.switch.0",
            "!board.KEYBOARD-L.switch.3",
            "board.KEYBOARD-L.switch.0",
            "!board.KEYBOARD-L.switch.0",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "C"),
            call("release", "C"),
            call("press", "E"),
            call("release", "E"),
            call("press", "A"),
            call("release", "A"),
        ]


class TestNestedCommands:
    @staticmethod
    def _setup(monkeypatch, events):
        # Hardware definition
        definition = {
            "hardware": {
                "KEYBOARD-L": {
                    "pins": {
                        "cols": (1, 2),
                        "rows": (1, 2),
                    },
                },
            },
            "layout": {
                "layers": {
                    "default": {
                        "keys": [
                            # fmt: off
            "TH_HD(A,LY_TO(1))",    "TH_HD(B,TH_HD(Y,Z))",
            "C",                    "TH_HD(B,TH_HD(V,TH_HD(W,X)))",
                            # fmt: on
                        ],
                    },
                    "1": {
                        "keys": [
                            # fmt: off
            "E",                        "F",
            "TH_TP(LY_TO(default), G)", "H",
                            # fmt: on
                        ],
                    },
                }
            },
            "settings": {
                "default_layer": "default",
            },
        }

        keyboard, action = make_keyboard(definition, monkeypatch)
        keyboard.board.get_event_controller = MagicMock(side_effect=events)
        event_delays = [0] * len(events)
        return keyboard, event_delays, action

    @classmethod
    def test_th_ly(cls, monkeypatch):
        events = [
            "board.KEYBOARD-L.switch.0",
            "!board.KEYBOARD-L.switch.0",
            "board.KEYBOARD-L.switch.1",
            "!board.KEYBOARD-L.switch.1",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        event_delays[1] = 0.4
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "F"),
            call("release", "F"),
        ]

    @classmethod
    def test_th_th_1(cls, monkeypatch):
        events = [
            "board.KEYBOARD-L.switch.1",
            "!board.KEYBOARD-L.switch.1",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "B"),
            call("release", "B"),
        ]

    @classmethod
    def test_th_th_2(cls, monkeypatch):
        events = [
            "board.KEYBOARD-L.switch.1",
            "!board.KEYBOARD-L.switch.1",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        event_delays[1] = 0.4
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "Y"),
            call("release", "Y"),
        ]

    @classmethod
    def test_th_th_3(cls, monkeypatch):
        events = [
            "board.KEYBOARD-L.switch.1",
            "!board.KEYBOARD-L.switch.1",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        event_delays[1] = 0.7
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "Z"),
            call("release", "Z"),
        ]

    @classmethod
    def test_th_th_th_4(cls, monkeypatch):
        events = [
            "board.KEYBOARD-L.switch.3",
            "!board.KEYBOARD-L.switch.3",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        event_delays[1] = 1.0
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "X"),
            call("release", "X"),
        ]


class TestMultiTap:
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
            "layout": {
                "layers": {
                    "default": {
                        "keys": [
                            # fmt: off
            "A",        "MT(B)",
            "MT(C,X)",  "MT(D,LY_MO(Layer1),TH_HD(Y,Z))",
                            # fmt: on
                        ],
                    },
                    "Layer1": {
                        "keys": [
                            # fmt: off
            "E",        "F",
            "G",        "H",
                            # fmt: on
                        ],
                    },
                }
            },
            "settings": {
                "default_layer": "default",
            },
        }

        keyboard, action = make_keyboard(definition, monkeypatch)
        keyboard.boards[0].get_event = MagicMock(side_effect=events)
        event_delays = [0] * len(events)
        return keyboard, event_delays, action

    @classmethod
    def test_no_multitap(cls, monkeypatch):
        events = [
            "board.test.switch.1",
            "!board.test.switch.1",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "B"),
            call("release", "B"),
        ]

    @classmethod
    def test_single_tap(cls, monkeypatch):
        events = [
            "board.test.switch.2",
            "!board.test.switch.2",
            "board.test.switch.0",
            "!board.test.switch.0",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "C"),
            call("release", "C"),
            call("press", "A"),
            call("release", "A"),
        ]

    @classmethod
    def test_double_tap(cls, monkeypatch):
        events = [
            "board.test.switch.2",
            "!board.test.switch.2",
            "board.test.switch.2",
            "!board.test.switch.2",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "X"),
            call("release", "X"),
        ]

    @classmethod
    def test_doulbetap_command(cls, monkeypatch):
        events = [
            "board.test.switch.3",
            "!board.test.switch.3",
            "board.test.switch.3",
            "board.test.switch.0",
            "!board.test.switch.0",
            "!board.test.switch.3",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "E"),
            call("release", "E"),
        ]

    @classmethod
    def test_triple_tap_taphold_tap(cls, monkeypatch):
        events = [
            "board.test.switch.3",
            "!board.test.switch.3",
            "board.test.switch.3",
            "!board.test.switch.3",
            "board.test.switch.3",
            "!board.test.switch.3",
            "board.test.switch.0",
            "!board.test.switch.0",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        event_delays[-1] = 0.4
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "Y"),
            call("release", "Y"),
            call("press", "A"),
            call("release", "A"),
        ]

    @classmethod
    def test_triple_tap_taphold_hold(cls, monkeypatch):
        events = [
            "board.test.switch.3",
            "!board.test.switch.3",
            "board.test.switch.3",
            "!board.test.switch.3",
            "board.test.switch.3",
            "!board.test.switch.3",
            "board.test.switch.0",
            "!board.test.switch.0",
        ]
        keyboard, event_delays, action = cls._setup(monkeypatch, events)
        event_delays[5] = 0.4
        run_scenario(keyboard, event_delays)
        assert action.call_args_list == [
            call("press", "Z"),
            call("release", "Z"),
            call("press", "A"),
            call("release", "A"),
        ]
