from unittest.mock import MagicMock, call

from explore.multiverse.timeline import Timeline


def test_new():
    """
    Test the creation of a Timeline
    """
    timeline_events = [(1, None)]
    timeline = Timeline(timeline_events)
    assert timeline.events == timeline_events
    assert timeline.output == []
    assert timeline.status == False


def test_split():
    """
    Test a timeline split
    """
    events = [(1, None), (2, None)]
    timeline = Timeline(events)
    timeline.output = ["A", "B"]
    timeline.status = True
    split_time = timeline.split()[-1]
    assert split_time.events == events
    assert split_time.output == timeline.output
    assert split_time.status == timeline.status


def test_simplekey_timeline():
    action = MagicMock()
    timeline_events = [(1, lambda: action("A")), (2, lambda: action("a"))]
    events = [1, 2]
    run_scenario(timeline_events, events)
    assert action.call_args_list == [call("A"), call("a")]


def run_scenario(timeline_events, events):
    # Reset Timeline
    Timeline.active_timelines.clear()
    Timeline.next_timeline = None

    # Run test
    Timeline(timeline_events)
    for event in events:
        Timeline.process_event(event)
