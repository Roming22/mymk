from mymk.feature.keys.key import Key
from mymk.feature.layers.layer_manager import LayerManager


class Timeline:
    def __init__(self, events, parent=None) -> None:
        """Create a new timeline

        events: an ordered list of expected events in the timeline. Each event
                is paired with the action that should be executed when the event
                is triggered, and an output action which is executed when the
                timeline is resolved.
                The timeline will be terminated if it receives an event that is
                not part of the timeline.
        output: an order list of actions that will be executed if the timeline
                is selected when all the timeline are resolved.
        determined: a boolean flag that indicates whether the timeline segment has
                come to some sort of resolution. This usually means that a character
                has been output or there was a layer change.
                A determined timeline will spawn new children timelines as
                new events are coming in.
        """
        self.what = events.pop("what")
        self.children = []
        self.determined = len(events) == 0 and parent is None
        self.events = events
        self.layers = []
        self.output = []
        self.next_timeline = None
        self.parent = parent

        if parent:
            parent.determined = True
            if parent.parent:
                parent.parent.next_timeline = parent
            for event, timeline in parent.events.items():
                self.events[event] = list(timeline)
            self.layers = parent.layers
            parent.children.append(self)

    def create_layer(self, layer_name: str):
        # TODO: layer should be a copy. Otherwise deactivate is going to cause issues
        layer = LayerManager.get(layer_name)

        # TODO: merge layers. Otherwise deactivating a lower layer will impact the current layer.

        return layer

    def activate(self, layer, is_root) -> None:
        print("Activate layer", layer.uid)
        if is_root:
            self.layers.clear()
        self.layers.append(layer)

    def deactivate(self, layer) -> None:
        print("Deactivate layer", layer.uid)
        self.layers.remove(layer)

    def load_events(self, universe, switch_uid) -> list:
        keycodes = []
        for layer in reversed(self.layers):
            keycodes = layer.switch_to_keycode[switch_uid]
            if keycodes:
                break

        timelines_events = []
        for keycode in keycodes:
            timelines_events += Key.load(switch_uid, keycode, universe)
        return timelines_events

    def prune(self) -> None:
        """Some timelines might be deadends. They are removed from the multiverse"""
        parent = self.parent
        if parent:
            self.parent = None
            parent.children.remove(self)
            if parent.next_timeline == self:
                parent.next_timeline = None
            if not parent.children:
                parent.prune()
