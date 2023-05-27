from mymk.feature.layers.layer import Layer


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
