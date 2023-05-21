from mymk.feature.key import Key

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

    def load_events(self, timeline, switch_uid):
        timelines_events = []
        for keycode in self.switch_to_keycode[switch_uid]:
            print(switch_uid, keycode)
            timelines_events += Key.load(switch_uid, keycode, timeline)
        return timelines_events


class LayerManager:
    _instances = {}

    @classmethod
    def load(cls, board_name, layer_name, definition) -> None:
        print("Layers:", cls._instances.keys())
        cls._instances[layer_name] = Layer(board_name, layer_name, definition)
        print(cls._instances[layer_name])

    @classmethod
    def activate(cls, layer_name, timeline) -> None:
        new_layer = cls._instances[layer_name]
        # old_layer = timeline.layer
        # if old_layer:
        #     new_layer = cls.merge(old_layer, new_layer)
        timeline.layer = new_layer

    # @staticmethod
    # def merge(old: Layer, new: Layer) -> None:
    #     board_name = new.switch_to_keycode.keys[0].split(".")[1]
    #     definition = []
    #     for switch_uid, keycode in new.switch_to_keycode.items():
    #         if keycode:
    #             definition.append(keycode)
    #         else:
    #             definition.append(old.switch_to_keycode[switch_uid])
    #     return Layer(board_name, new.name, definition)
