from mymk.feature.keys.combo import load_combo
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
            for combo_definition, keycode in layer_definition["combos"].items():
                combos = load_combo(switch_prefix, combo_definition, keycode)
                for switch_uid, keycode in combos:
                    if switch_uid not in self.switch_to_keycode.keys():
                        self.switch_to_keycode[switch_uid] = []
                    self.switch_to_keycode[switch_uid].append(keycode)
                    print("Added combo:", keycode)
        else:
            print("No combo has been declared in layer", layer_name)

    def load_events(self, universe, switch_uid) -> list:
        timelines_events = []
        for keycode in self.switch_to_keycode[switch_uid]:
            # print(switch_uid, keycode)
            timelines_events += Key.load(switch_uid, keycode, universe)
        return timelines_events
