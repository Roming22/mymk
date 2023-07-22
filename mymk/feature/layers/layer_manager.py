from mymk.feature.layers.layer import Layer

# from mymk.utils.logger import logger


class LayerManager:
    _instances = {}

    @classmethod
    def load(cls, board: "Board", layer_name: str, definition: dict) -> None:
        # logger.info("Layers: %s", cls._instances.keys())
        cls._instances[layer_name] = Layer(board, layer_name, definition)
        # logger.info(cls._instances[layer_name])

    @classmethod
    def get(cls, layer_name: str) -> Layer:
        return cls._instances[layer_name]
