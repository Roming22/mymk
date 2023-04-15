import re

from seaks.features.key import (
    func_mapping,
    press_patterns,
    regex_cache,
    release_patterns,
)
from seaks.features.key import set as Key
from seaks.logic.action import Action
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

    @classmethod
    def to(cls, layer_name: str):
        active_layer = ActiveLayer(cls.LAYERS[layer_name])
        ActiveLayer.collapse()
        return active_layer.deactivate


def layer_to(key_uid: str, layer_name: list[str]) -> None:
    switch_uid = ".".join(key_uid.split(".")[-2:])
    press_event_uid = key_uid
    release_event_uid = f"!{key_uid}"
    release_event_id = f"!{switch_uid}"

    regex_cache[press_event_uid] = re.compile(f"^(.*/)?{press_event_uid}(/.*)?$")
    regex_cache[release_event_uid] = re.compile(f"^(.*/)?{release_event_id}(/.*)?$")

    release_action = Action.chain(
        Action(lambda: release_patterns.pop(release_event_uid)),
        Action.claim(release_event_id),
    )
    press_action = Action.chain(
        Action(lambda: release_patterns.update({release_event_uid: release_action})),
        Action(lambda: Layer.to(layer_name[0])),
        Action.claim(press_event_uid),
    )

    press_patterns[1][press_event_uid] = press_action


def layer_momentary(key_uid: str, layer_name: list[str]) -> None:
    switch_uid = ".".join(key_uid.split(".")[-2:])
    press_event_uid = key_uid
    release_event_uid = f"!{key_uid}"
    release_event_id = f"!{switch_uid}"

    regex_cache[press_event_uid] = re.compile(f"^(.*/)?{press_event_uid}(/.*)?$")
    regex_cache[release_event_uid] = re.compile(f"^(.*/)?{release_event_id}(/.*)?$")

    def activate():
        deactivate = Layer.activate_layer(layer_name[0])
        release_action = Action.chain(
            Action(lambda: release_patterns.pop(release_event_uid)),
            Action(deactivate),
            Action.claim(release_event_id),
        )
        release_patterns.update({release_event_uid: release_action})

    press_action = Action.chain(
        Action(activate),
        Action.claim(press_event_uid),
    )

    press_patterns[1][press_event_uid] = press_action


func_mapping["LY_TO"] = layer_to
func_mapping["LY_MO"] = layer_momentary
