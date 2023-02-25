from seaks.state import StateMachine


class Layer(StateMachine):
    layers = {}

    def __init__(self, state_names: list[str], name: str = "layer") -> None:
        super().__init__(name, state_names, True)
        for name in state_names:
            self.layers[name] = {}

    def set_key(self, layer_name: str, key) -> None:
        if key in self.layers[layer_name].keys():
            # Unregister the existing key to ensure that a switch does not manage multiple keys
            pass
        self.layers[layer_name][key.name] = key
