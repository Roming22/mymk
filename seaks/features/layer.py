class ActiveLayer:
    LAYERS: list["ActiveLayer"] = []

    def __init__(self, layer: list) -> None:
        self.LAYERS.append(self)
        self.id = layer.id
        self.uid = f"{layer.id}|{self.__hash__[:4]}"
        self.keys_to_layer = [layer.id if k is not None else None for k in layer.keys]
        self.freeze()
        print(f"Activating Layer '{self.uid}'. Layers: {[l.uid for l in self.LAYERS]}")

    def freeze(self) -> None:
        """Freeze transparent keys
        This allows lower layer to be deactivated while keeping
        the top layer key configuration.

        E.g if Layer1 is activated, then Layer2 is activated,
        then Layer1 is deactivated; Layer2 should still forward
        transparent keys to Layer1.
        """
        current_layer = self.LAYERS[:-1]
        for index, key in self.keys:
            if key is None:
                self.keys[index] = current_layer.keys[index]

    def deactivate(self):
        """Remove layer from the list of active layers"""
        is_top_layer = self.LAYERS[:-1] == self
        self.LAYERS.remove(self)
        print(
            f"Deactivating Layer '{self.uid}'. Layers: {[l.uid for l in self.LAYERS]}"
        )

        # If the top layer is being deactivated, the next active
        # layer needs to be activated.
        if is_top_layer:
            # Keys.activate(self.LAYERS[:-2])
            print(f"Fallbacking to Layer '{self.uid}'")

    @classmethod
    def get_layer_for(cls, switch_id: int) -> str:
        """Get the layer"""
        current_layer = cls.LAYERS[:-1]
        return current_layer.keys_to_layer[switch_id]


class Layer:
    """Holds the layer definition"""

    LAYERS = []

    def __init__(self, layer_definition) -> None:
        self.LAYERS.append(self)
        self.id = len(self.LAYERS)
        self.keys = []

        for key in layer_definition["keys"]:
            self.keys.append(key)

        # Check that the first layer has no transparent key.
        if self.id == 0 and None in self.keys:
            raise RuntimeError("Transparent keys not allowed on Layer 0.")

    @classmethod
    def activate_layer(cls, layer_id: str):
        active_layer = ActiveLayer(cls.LAYERS[layer_id])
        return active_layer.deactivate
