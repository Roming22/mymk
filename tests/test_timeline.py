from unittest.mock import MagicMock, call

from mymk.multiverse.timeline import Timeline
from mymk.multiverse.timeline_manager import TimelineManager


class TestTimelineManager:
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

        multiverse = TimelineManager()
        multiverse.start(timeline)

        assert multiverse.timeline_start == timeline
        assert multiverse.active_timelines == [timeline]
        assert multiverse.current_timeline is None

    @staticmethod
    def test_split():
        """
        Test a timeline split
        """
        timeline = Timeline([])
        timeline.output = ["A", "B"]
        multiverse = TimelineManager()
        multiverse.start(timeline)
        events_list = [
            {
                "events": [("timelineA", None, None)],
            },
            {
                "events": [("timelineB", None, None)],
            },
            {
                "events": [("timelineC", None, None)],
            },
        ]

        multiverse.current_timeline = timeline
        multiverse.split(events_list)

        assert timeline.determined == True
        assert len(timeline.children) == len(events_list)

        for child in timeline.children:
            assert child.events == events_list.pop(0)["events"]
            assert child.output == timeline.output
            assert child.determined == False

        assert multiverse.timeline_start == timeline
        assert timeline not in multiverse.active_timelines
        assert multiverse.active_timelines == timeline.children


class TestSimpleKey:
    def test_simplekey_timeline(_):
        do = MagicMock()
        timeline_events = [
            ("press", lambda: do("A"), None),
            ("release", lambda: do("a"), None),
        ]
        timeline = Timeline(timeline_events)
        multiverse = TimelineManager()
        multiverse.start(timeline)

        events = ["press", "release"]
        run_scenario(events)
        assert do.call_args_list == [call("A"), call("a")]


class TestTapHold:
    @staticmethod
    def setup():
        do = MagicMock()
        multiverse = TimelineManager()
        timeline_events = [
            (
                "press",
                lambda: multiverse.split(
                    [
                        {
                            "action": None,
                            "events": [("release", None, lambda: do("a"))],
                            "output": lambda: do("A"),
                        },
                        {
                            "action": None,
                            "events": [
                                ("hold", None, lambda: do("B")),
                                ("release", None, lambda: do("b")),
                            ],
                            "output": lambda: do("Start timer"),
                        },
                        {
                            "events": [
                                ("interrupt", None, lambda: do("C")),
                                ("release", None, lambda: do("c")),
                            ],
                        },
                    ]
                ),
                None,
            )
        ]
        multiverse.start(Timeline(timeline_events))
        return multiverse, do

    def test_tap_key_timeline(self):
        events = ["press", "release"]
        multiverse, do = self.setup()
        run_scenario(events)
        assert do.call_args_list == [call("A"), call("a")]

    def test_hold_key_timeline(self):
        events = ["press", "hold", "release"]
        multiverse, do = self.setup()
        run_scenario(events)
        assert do.call_args_list == [call("Start timer"), call("B"), call("b")]

    def test_interrupt_key_timeline(self):
        events = ["press", "interrupt", "release"]
        multiverse, do = self.setup()
        run_scenario(events)
        assert do.call_args_list == [call("C"), call("c")]


class TestCombo:
    @staticmethod
    def setup():
        do = MagicMock()
        multiverse = TimelineManager()
        timeline_events = [
            (
                "switch.1",
                lambda: multiverse.split(
                    [
                        # Simple key
                        {
                            "events": [],
                            "output": lambda: do("A"),
                        },
                        # 1+2 = B
                        {
                            "events": [("switch.2", None, lambda: do("B"))],
                        },
                        # 1+3 = C
                        {
                            "events": [("switch.3", None, lambda: do("C"))],
                        },
                        # 1+2+3 = D
                        {
                            "events": [
                                ("switch.2", None, None),
                                ("switch.3", None, lambda: do("D")),
                            ],
                        },
                        # 1+3+2 = E
                        {
                            "events": [
                                ("switch.3", None, None),
                                ("switch.2", None, lambda: do("E")),
                            ],
                        },
                    ]
                ),
                None,
            )
        ]
        multiverse.start(Timeline(timeline_events))
        return multiverse, do

    def test_1(self):
        events = ["switch.1", "the start of something new"]
        multiverse, do = self.setup()
        run_scenario(events)
        assert do.call_args_list == [call("A")]

    def test_1_2(self):
        events = ["switch.1", "switch.2", "the start of something new"]
        multiverse, do = self.setup()
        run_scenario(events)
        assert do.call_args_list == [call("B")]

    def test_1_3(self):
        events = ["switch.1", "switch.3", "timeout of combo 1+3+2"]
        multiverse, do = self.setup()
        run_scenario(events)
        assert do.call_args_list == [call("C")]

    def test_1_2_3(self):
        events = ["switch.1", "switch.2", "switch.3"]
        multiverse, do = self.setup()
        run_scenario(events)
        assert do.call_args_list == [call("D")]

    def test_1_3_2(self):
        events = ["switch.1", "switch.3", "switch.2"]
        multiverse, do = self.setup()
        run_scenario(events)
        assert do.call_args_list == [call("E")]


def run_scenario(events):
    # Run test
    for event in events:
        TimelineManager.process_event(event)
