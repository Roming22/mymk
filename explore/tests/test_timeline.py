import unittest

from multiverse.timeline import Timeline


class TestTimeline(unittest.TestCase):
    def test_new(self):
        """
        Test the creation of a Timeline
        """
        events = [1, 2, 3]
        timeline = Timeline(events)
        self.assertEqual(timeline.events, [1, 2, 3])
        self.assertEqual(timeline.output, [])
        self.assertEqual(timeline.status, False)

    def test_split(self):
        """
        Test a timeline split
        """
        events = [1, 2, 3]
        timeline = Timeline(events)
        timeline.output=["A", "B"]
        timeline.status = True
        split_time = timeline.split()[-1]
        self.assertEqual(split_time.events, [1, 2, 3])
        self.assertEqual(split_time.output, timeline.output)
        self.assertEqual(split_time.status, timeline.status)

if __name__ == '__main__':
    unittest.main()
