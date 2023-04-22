from seaks.features.key import action_func, func_mapping
from seaks.features.key import set as Key
from seaks.features.key import set_key
from seaks.logic.buffer import Buffer
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
        if len(self.LAYERS) > 1:
            self.refresh_buffer(self.LAYERS[-2].id)

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

    @classmethod
    def collapse(cls) -> None:
        layers = [cls.LAYERS[0]]
        if cls.LAYERS[-1].id != layers[0].id:
            layers.append(cls.LAYERS[-1])
        print(f"Collapsing layers: {[l.uid for l in layers]}")
        cls.LAYERS = layers

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
            self.refresh_buffer(self.id)

    @classmethod
    def get_layer_for(cls, switch_id: int) -> str:
        """Get the layer"""
        current_layer = cls.LAYERS[-1]
        return current_layer.keys_to_layer[switch_id]

    @classmethod
    def refresh_buffer(cls, layer_name) -> None:
        for index, event in enumerate(Buffer.instance.content):
            new_event = event.replace(layer_name, cls.LAYERS[-1].id)
            Buffer.instance.content[index] = new_event
        Buffer.instance.update_data()


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
        print()

        # Check that the first layer has no transparent key.
        if self.id == 0 and None in self.keys:
            raise RuntimeError("Transparent keys not allowed on Layer 0.")

    @classmethod
    def activate_layer(cls, layer_name: str):
        active_layer = ActiveLayer(cls.LAYERS[layer_name])
        return active_layer.deactivate

    @classmethod
    def to(cls, layer_name: str):
        active_layer = ActiveLayer(cls.LAYERS[layer_name])
        ActiveLayer.collapse()
        return active_layer.deactivate


@memory_cost("LY_TO")
def layer_to(key_uid: str, layer_name: str) -> None:
    print("GNRX", layer_name)
    set_key(key_uid, *get_to_action(layer_name))


@memory_cost("LY_MO")
def layer_momentary(key_uid: str, layer_name: str) -> None:
    set_key(key_uid, *get_momentary_action(layer_name))


@memory_cost("LY_TG")
def layer_toggle(key_uid: str, layer_name: str) -> None:
    set_key(key_uid, *get_toggle_action(layer_name))


def make_toggle(layer_name: str):
    def make_func():
        deactivate = None

        def toggle():
            nonlocal deactivate
            if deactivate:
                print("Toggle OFF")
                deactivate()
                deactivate = None
            else:
                print("Toggle ON")
                deactivate = Layer.activate_layer(layer_name)

        return toggle

    return make_func()


def get_momentary_action(layer_name: str):
    toggle = make_toggle(layer_name)
    return (toggle, toggle)


def get_toggle_action(layer_name: str):
    on_release = lambda: True
    on_press = make_toggle(layer_name)
    return (on_press, on_release)


def get_to_action(layer_name: str):
    on_release = lambda: True
    on_press = lambda: Layer.to(layer_name)
    return (on_press, on_release)


func_mapping["LY_MO"] = layer_momentary
func_mapping["LY_TG"] = layer_toggle
func_mapping["LY_TO"] = layer_to

action_func["LY_MO"] = get_momentary_action
action_func["LY_TG"] = get_toggle_action
action_func["LY_TO"] = get_to_action
