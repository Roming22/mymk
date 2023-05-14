from unittest.mock import MagicMock, call

from explore.multiverse.timeline import Timeline


class TestTimeline:
    @staticmethod
    def test_new():
        """
        Test the creation of a Timeline
        """
        reset_timeline_class()

        timeline_events = [(1, None, None)]
        timeline = Timeline(timeline_events)
        assert timeline.events == timeline_events
        assert timeline.output == []
        assert timeline.determined == False

        assert Timeline.timeline_start == timeline
        assert Timeline.active_timelines == [timeline]
        assert Timeline.current_timeline is None

    @staticmethod
    def test_split():
        """
        Test a timeline split
        """
        reset_timeline_class()

        timeline = Timeline([])
        timeline.output = ["A", "B"]
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

        Timeline.current_timeline = timeline
        Timeline.split(events_list)

        assert timeline.determined == True
        assert len(timeline.children) == len(events_list)

        for child in timeline.children:
            assert child.events == events_list.pop(0)["events"]
            assert child.output == timeline.output
            assert child.determined == False

        assert Timeline.timeline_start == timeline
        assert timeline not in Timeline.active_timelines
        assert Timeline.active_timelines == timeline.children


class TestSimpleKey:
    def test_simplekey_timeline(_):
        do = MagicMock()
        timeline_events = [
            ("press", lambda: do("A"), None),
            ("release", lambda: do("a"), None),
        ]
        events = ["press", "release"]
        run_scenario(timeline_events, events)
        assert do.call_args_list == [call("A"), call("a")]


class TestTapHold:
    @staticmethod
    def get_timeline_events():
        do = MagicMock()
        timeline_events = [
            (
                "press",
                lambda: Timeline.split(
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
        return do, timeline_events

    def test_tap_key_timeline(self):
        do, timeline_events = self.get_timeline_events()
        events = ["press", "release"]
        run_scenario(timeline_events, events)
        assert do.call_args_list == [call("A"), call("a")]

    def test_hold_key_timeline(self):
        do, timeline_events = self.get_timeline_events()
        events = ["press", "hold", "release"]
        run_scenario(timeline_events, events)
        assert do.call_args_list == [call("Start timer"), call("B"), call("b")]

    def test_interrupt_key_timeline(self):
        do, timeline_events = self.get_timeline_events()
        events = ["press", "interrupt", "release"]
        run_scenario(timeline_events, events)
        assert do.call_args_list == [call("C"), call("c")]

class TestCombo:
    @staticmethod
    def get_timeline_events():
        do = MagicMock()
        timeline_events = [
            (
                "switch.1",
                lambda: Timeline.split(
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
                            "events": [("switch.2", None, None),("switch.3", None, lambda: do("D"))],
                        },
                        # 1+3+2 = E
                        {
                            "events": [("switch.3", None, None),("switch.2", None, lambda: do("E"))],
                        },
                    ]
                ),
                None,
            )
        ]
        return do, timeline_events

    def test_1(self):
        do, timeline_events = self.get_timeline_events()
        events = ["switch.1", "the start of something new"]
        run_scenario(timeline_events, events)
        assert do.call_args_list == [call("A")]

    def test_1_2(self):
        do, timeline_events = self.get_timeline_events()
        events = ["switch.1", "switch.2", "the start of something new"]
        run_scenario(timeline_events, events)
        assert do.call_args_list == [call("B")]

    def test_1_3(self):
        do, timeline_events = self.get_timeline_events()
        events = ["switch.1", "switch.3", "timeout of combo 1+3+2"]
        run_scenario(timeline_events, events)
        assert do.call_args_list == [call("C")]

    def test_1_2_3(self):
        do, timeline_events = self.get_timeline_events()
        events = ["switch.1", "switch.2", "switch.3"]
        run_scenario(timeline_events, events)
        assert do.call_args_list == [call("D")]

    def test_1_3_2(self):
        do, timeline_events = self.get_timeline_events()
        events = ["switch.1", "switch.3", "switch.2"]
        run_scenario(timeline_events, events)
        assert do.call_args_list == [call("E")]

def reset_timeline_class():
    Timeline.active_timelines.clear()
    Timeline.current_timeline = None
    Timeline.timeline_start = None


def run_scenario(timeline_events, events):
    # Reset Timeline
    reset_timeline_class()

    # Run test
    Timeline(timeline_events)
    for event in events:
        Timeline.process_event(event)
