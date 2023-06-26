from mymk.feature.layers.layer import Layer
from mymk.utils.logger import logger


class LayerManager:
    _instances = {}

    @classmethod
    def load(
        cls, board_name: str, layer_name: str, definition: dict, pixels: "NeoPixel"
    ) -> None:
        # logger.info("Layers: %s", cls._instances.keys())
        cls._instances[layer_name] = Layer(board_name, layer_name, definition, pixels)
        # logger.info(cls._instances[layer_name])

    @classmethod
    def get(cls, layer_name):
        return cls._instances[layer_name]
