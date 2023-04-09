from seaks.features.key import set as Key
from seaks.utils.memory import memory_cost


class ActiveLayer:
    LAYERS: list["ActiveLayer"] = []

    @memory_cost("ActiveLayer")
    def __init__(self, layer: list) -> None:
        self.id = layer.id
        self.uid = f"{layer.id}|{id(self)}"
        self.keys_to_layer = list(layer.keys_to_layer)
        self.freeze()
        self.LAYERS.append(self)
        print(f"Activating Layer '{self.uid}'. Layers: {[l.uid for l in self.LAYERS]}")

    def freeze(self) -> None:
        """Freeze transparent keys
        This allows lower layer to be deactivated while keeping
        the top layer key configuration.

        E.g if Layer1 is activated, then Layer2 is activated,
        then Layer1 is deactivated; Layer2 should still forward
        transparent keys to Layer1.
        """
        try:
            current_layer = self.LAYERS[-1]
        except IndexError:
            current_layer = None
        for index, key_to_layer in enumerate(self.keys_to_layer):
            if key_to_layer is None:
                if current_layer is None:
                    raise RuntimeError(
                        f"Layer '{self.id}' cannot have a transparent key."
                    )
                self.keys_to_layer[index] = current_layer.keys_to_layer[index]

    def deactivate(self):
        """Remove layer from the list of active layers"""
        is_top_layer = self is self.LAYERS[-1]
        self.LAYERS.remove(self)
        print(
            f"Deactivating Layer '{self.uid}'. Layers: {[l.uid for l in self.LAYERS]}"
        )

        # If the top layer is being deactivated, the next active
        # layer is now activated.
        if is_top_layer:
            print(f"Fallbacking to Layer '{self.LAYERS[-1].uid}'")

    @classmethod
    def get_layer_for(cls, switch_id: int) -> str:
        """Get the layer"""
        current_layer = cls.LAYERS[-1]
        return current_layer.keys_to_layer[switch_id]


class Layer:
    """Holds the layer definition"""

    LAYERS = {}

    @memory_cost("Layer")
    def __init__(self, board, layer_name: str, layer_definition) -> None:
        print(layer_name, end=":")
        self.LAYERS[layer_name] = self
        self.uid = f"{board.name}.{layer_name}"
        self.id = layer_name
        self.keys_to_layer = []
        for switch_id, keycode in enumerate(layer_definition["keys"]):
            if keycode is None:
                self.keys_to_layer.append(None)
            else:
                self.keys_to_layer.append(layer_name)
            Key(
                self.uid,
                board.hardware_board.get_switch_id(switch_id),
                keycode,
            )
            print(f" {keycode}", end=",")
        print()

        # Check that the first layer has no transparent key.
        if self.id == 0 and None in self.keys:
            raise RuntimeError("Transparent keys not allowed on Layer 0.")

    @classmethod
    def activate_layer(cls, layer_name: str):
        active_layer = ActiveLayer(cls.LAYERS[layer_name])
        return active_layer.deactivate
