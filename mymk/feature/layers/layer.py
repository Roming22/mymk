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

    @staticmethod
    def split_timeline_momentary(universe, switch_uid, data) -> None:
        layer_name = data[0]

        events = {"what": f"{switch_uid} press/release {layer_name}"}
        timeline = universe.split(events)

        layer = timeline.activate(layer_name, False)
        deactivate_layer = lambda: timeline.deactivate(layer)
        timeline.events[f"!{switch_uid}"] = [(f"!{switch_uid}", [], [deactivate_layer])]
        timeline.mark_determined()

    @staticmethod
    def split_timeline_to(universe, switch_uid, data) -> None:
        layer_name = data[0]

        events = {"what": f"{switch_uid} press/release {layer_name}"}
        timeline = universe.split(events)

        timeline.activate(layer_name, True)
        timeline.events[f"!{switch_uid}"] = [(f"!{switch_uid}", [], [])]
        timeline.mark_determined()


Key.loader_map["LY_MO"] = Layer.split_timeline_momentary
Key.loader_map["LY_TO"] = Layer.split_timeline_to
