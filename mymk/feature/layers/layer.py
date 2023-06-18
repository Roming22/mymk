from mymk.feature.keys.combo import load_combos
from mymk.feature.keys.key import Key
from mymk.utils.memory import memory_cost


class Layer:
    """Holds the layer definition"""

    @memory_cost("Layer")
    def __init__(self, board_name, layer_name: str, layer_definition) -> None:
        print("Loading layer:", layer_name)
        self.uid = f"board.{board_name}.layer.{layer_name}"
        self.switch_to_keycode = {}
        switch_prefix = f"board.{board_name}.switch"
        for switch_id, keycode in enumerate(layer_definition["keys"]):
            switch_uid = f"{switch_prefix}.{switch_id}"
            self.switch_to_keycode[switch_uid] = [keycode]

        # Load combos
        if "combos" in layer_definition.keys():
            combos = load_combos(switch_prefix, layer_definition["combos"])
            for switch_uid, keycode in combos:
                if switch_uid not in self.switch_to_keycode.keys():
                    self.switch_to_keycode[switch_uid] = []
                self.switch_to_keycode[switch_uid].append(keycode)
                print("Added combo:", keycode)
        else:
            print("No combo has been declared in layer", layer_name)

    @classmethod
    def get_momentary_action(cls, universe, switch_uid, data):
        layer_name = data[0]
        timeline = universe.current_timeline
        layer = timeline.create_layer(layer_name)
        activate_layer = lambda: timeline.activate(layer, False)
        deactivate_layer = lambda: timeline.deactivate(layer)

        timeline_events = [
            {
                "what": f"{switch_uid} press/release",
                switch_uid: [
                    (
                        switch_uid,
                        [universe.mark_determined],
                        [activate_layer],
                    ),
                    (
                        f"!{switch_uid}",
                        [],
                        [deactivate_layer],
                    ),
                ],
            },
        ]
        return timeline_events

    @classmethod
    def get_to_action(cls, universe, switch_uid, data):
        layer_name = data[0]
        timeline = universe.current_timeline
        layer = timeline.create_layer(layer_name)
        activate_layer = lambda: timeline.activate(layer, True)
        timeline_events = [
            {
                "what": f"{switch_uid} press/release",
                switch_uid: [
                    (
                        switch_uid,
                        [universe.mark_determined],
                        [activate_layer],
                    ),
                    (f"!{switch_uid}", [], None),
                ],
            },
        ]
        return timeline_events


Key.loader_map["LY_MO"] = Layer.get_momentary_action
Key.loader_map["LY_TO"] = Layer.get_to_action
