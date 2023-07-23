from mymk.feature.layers.layer import Layer

# from mymk.utils.logger import logger

_instances = {}


def load(board: "Board", layer_name: str, definition: dict) -> None:
    # logger.info("Layers: %s", _instances.keys())
    _instances[layer_name] = Layer(board, layer_name, definition)
    # logger.info(_instances[layer_name])


def get(layer_name: str) -> Layer:
    return _instances[layer_name]
