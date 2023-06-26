from mymk.feature.keys.combo import load_combos
from mymk.logic.keys import loader_map
from mymk.utils.logger import logger
from mymk.utils.memory import memory_cost


class Layer:
    """Holds the layer definition"""

    # @memory_cost("Layer")
    def __init__(
        self, board_name, layer_name: str, layer_definition: dict, pixels=None
    ) -> None:
        logger.info("Loading layer: %s", layer_name)

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
                # logger.info("Added combo: %s", keycode)
        # else:
        #     logger.info("No combo has been declared in layer %s", layer_name)


def load_layer(mode: str, universe, switch_uid: str, data: list[str]) -> None:
    layer_name = data[0]
    print("Layer:", layer_name)
    timeline = universe.split(f"{switch_uid}.layer.{mode}.{layer_name}")
    layer = timeline.activate(layer_name, False)
    action = []
    if mode == "momentary":
        deactivate_layer = lambda: timeline.deactivate(layer)
        action.append(deactivate_layer)
    timeline.events[f"!{switch_uid}"] = [(f"!{switch_uid}", action, [])]
    timeline.mark_determined()


loader_map["LY_MO"] = lambda *args, **kwargs: load_layer("momentary", *args, **kwargs)
loader_map["LY_TO"] = lambda *args, **kwargs: load_layer("to", *args, **kwargs)
