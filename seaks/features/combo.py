from seaks.logic.timer import Timer
from seaks.utils.memory import memory_cost
from seaks.utils.toolbox import permutations

delay = [0.1]


@memory_cost("Combos")
def load_combos(definitions: dict) -> None:
    print("Loading combos")
    if "sequences" not in definitions.keys():
        definitions["sequences"] = {}

    # Expand chords to sequences
    for chord, keycode in definitions.get("chords", {}).items():
        for sequence in permutations(chord.split("+")):
            sequence_id = "+".join(sequence)
            # Do not allow a chord to override a user defined sequence
            if sequence_id not in definitions["sequences"].keys():
                definitions["sequences"][sequence_id] = keycode

    # Load all sequences
    for sequence, keycode in definitions["sequences"].items():
        load_sequence(sequence, keycode)


def load_sequence(sequence, keycode) -> None:
    print(sequence, keycode)
