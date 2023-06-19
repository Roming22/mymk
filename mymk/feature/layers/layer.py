from mymk.feature.keys.combo import load_combos
from mymk.logic.keys import loader_map
from mymk.utils.memory import memory_cost
from mymk.utils.toolbox import debug


class Layer:
    """Holds the layer definition"""

    # @memory_cost("Layer")
    def __init__(
        self, board_name, layer_name: str, layer_definition: dict, pixels=None
    ) -> None:
        debug("Loading layer:", layer_name)

        if pixels:
            color = layer_definition.get("leds", {}).get("RGB", (127, 127, 127))
            self.set_leds = lambda: pixels.fill(color)
        else:
            self.set_leds = lambda: None
        self.uid = f"board.{board_name}.layer.{layer_name}"
        self.switch_to_keycode = {}
        switch_prefix = f"board.{board_name}.switch"
        for switch_id, keycode in enumerate(layer_definition["keys"]):
            switch_uid = f"{switch_prefix}.{switch_id}"
            self.switch_to_keycode[switch_uid] = [keycode]

        # Load combos
        if "combos" in layer_definition.keys():
            combos = load_combos(switch_prefix, layer_definition["combos"])
            for switch_uid, keycode in combos:
                if switch_uid not in self.switch_to_keycode.keys():
                    self.switch_to_keycode[switch_uid] = []
                self.switch_to_keycode[switch_uid].append(keycode)
                # print("Added combo:", keycode)
        # else:
        #     print("No combo has been declared in layer", layer_name)


def load_layer(mode: str, universe, switch_uid: str, data: list[str]) -> None:
    layer_name = data[0]

    events = f"{switch_uid} press/release {layer_name}"
    timeline = universe.split(events)

    layer = timeline.activate(layer_name, False)
    output = []
    if mode == "momentary":
        deactivate_layer = lambda: timeline.deactivate(layer)
        output.append(deactivate_layer)
    timeline.events[f"!{switch_uid}"] = [(f"!{switch_uid}", [], output)]
    timeline.mark_determined()


loader_map["LY_MO"] = lambda *args, **kwargs: load_layer("momentary", *args, **kwargs)
loader_map["LY_TO"] = lambda *args, **kwargs: load_layer("to", *args, **kwargs)
