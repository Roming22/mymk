from mymk.feature.layers.layer import Layer


class LayerManager:
    _instances = {}

    @classmethod
    def load(cls, board_name: str, layer_name: str, definition: dict) -> None:
        print("Layers:", cls._instances.keys())
        cls._instances[layer_name] = Layer(board_name, layer_name, definition)
        print(cls._instances[layer_name])

    @classmethod
    def get(cls, layer_name):
        return cls._instances[layer_name]
