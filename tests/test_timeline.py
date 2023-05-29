from unittest.mock import MagicMock, call

import pytest

from mymk.feature.layers.layer_manager import LayerManager
from mymk.multiverse.timeline import Timeline
from mymk.multiverse.timeline_manager import TimelineManager

LayerManager.load("test", "empty", {"keys": []})


class Test_1_TimelineManager:
    @staticmethod
    def test_new():
        """
        Test the creation of a Timeline
        """
        timeline_events = [
            (
                "event1",
                lambda: "action on match".split(),
                lambda: "action on resolution".split(),
            )
        ]
        timeline = Timeline(timeline_events)

        assert timeline.events == timeline_events
        assert timeline.output == []
        assert timeline.determined == False

        TimelineManager._universes.clear()
        universe = TimelineManager(timeline)

        assert universe.timeline_start == timeline
        assert universe.active_timelines == [timeline]
        assert universe.current_timeline == timeline

    @staticmethod
    def test_split():
        """
        Test a timeline split
        """
        timeline = Timeline({})
        timeline.output = ["A", "B"]
        TimelineManager._universes.clear()
        universe = TimelineManager(timeline)
        events_list = [
            {
                "press": [("timelineA", None, None)],
            },
            {
                "press": [("timelineB", None, None)],
            },
            {
                "press": [("timelineC", None, None)],
            },
        ]

        universe.current_timeline = timeline
        for events in events_list:
            universe.split(events)

        assert timeline.determined == True
        assert len(timeline.children) == len(events_list)

        for child in timeline.children:
            assert child.events == events_list.pop(0)
            assert child.output == []
            assert child.determined == False

        assert universe.timeline_start == timeline
        assert timeline not in universe.active_timelines
        assert universe.active_timelines == timeline.children


class Test_2_SimpleKey:
    @staticmethod
    def test_simplekey_timeline():
        TimelineManager._universes.clear()
        universe = TimelineManager()

        do = MagicMock()
        timeline_events = {
            "press": [
                ("press", universe.mark_determined, lambda: do("A")),
                ("release", None, lambda: do("a")),
            ]
        }

        universe.split(timeline_events)
        events = ["press", "release"]
        run_scenario(events)
        assert do.call_args_list == [call("A"), call("a")]


class Test_3_TapHold:
    @pytest.fixture
    def action(_) -> MagicMock:
        TimelineManager._universes.clear()
        TimelineManager.activate("empty")
        universe = TimelineManager._universes[0]
        action = MagicMock()

        def exec(*args):
            def func():
                action(*args)

            return func

        timelines_events = [
            {
                "switch.1": [
                    ("switch.1", universe.mark_determined, exec("A")),
                    ("!switch.1", None, exec("a")),
                ],
            },
            {
                "switch.1": [
                    ("switch.1", exec("Start timer"), exec("B")),
                    ("timer.hold", universe.mark_determined, None),
                    ("!switch.1", None, exec("b")),
                ],
            },
            {
                "switch.1": [
                    ("switch.1", None, exec("C")),
                    ("interrupt", universe.mark_determined, None),
                    ("!switch.1", None, exec("c")),
                ],
            },
        ]
        for timeline_events in timelines_events:
            universe.split(timeline_events)
        assert len(universe.active_timelines) == len(timelines_events)

        return action

    @classmethod
    def test_tap_key_timeline(cls, action):
        events = ["switch.1", "!switch.1"]
        run_scenario(events)
        assert action.call_args_list == [call("Start timer"), call("A"), call("a")]

    @classmethod
    def test_hold_key_timeline(cls, action):
        events = ["switch.1", "timer.hold", "!switch.1"]
        run_scenario(events)
        assert action.call_args_list == [call("Start timer"), call("B"), call("b")]

    @classmethod
    def test_interrupt_key_timeline(cls, action):
        events = ["switch.1", "interrupt", "!switch.1"]
        run_scenario(events)
        assert action.call_args_list == [call("Start timer"), call("C"), call("c")]


def run_scenario(events):
    # Run test
    for event in events:
        TimelineManager.process_event(event)
