from mymk.feature.keys.key import Key

# from seaks.features.combo import load_combos
# from seaks.features.key import action_func
from mymk.utils.memory import memory_cost


class Layer:
    """Holds the layer definition"""

    @memory_cost("Layer")
    def __init__(self, board_name, layer_name: str, layer_definition) -> None:
        print("Loading layer:", layer_name)
        self.uid = f"board.{board_name}.layer.{layer_name}"
        self.switch_to_keycode = {}
        for switch_id, keycode in enumerate(layer_definition["keys"]):
            switch_uid = f"board.{board_name}.switch.{switch_id}"
            self.switch_to_keycode[switch_uid] = [keycode]

        # Load combos
        # try:
        #     load_combos(self.uid, layer_definition["combos"])
        # except KeyError:
        #     print("No combo has been declared")

    def load_events(self, universe, switch_uid):
        timelines_events = []
        for keycode in self.switch_to_keycode[switch_uid]:
            print(switch_uid, keycode)
            timelines_events += Key.load(switch_uid, keycode, universe)
        return timelines_events
