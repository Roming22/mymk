from seaks.buffer import Buffer
from seaks.hardware.keys import oneshot, press, release


class TapHold:
    def __init__(self, tap_key_name: str, hold_key_name) -> None:
        tap_key_name, hold_key_name = str.upper(tap_key_name), str.upper(hold_key_name)
        print(f"TapHold: '{tap_key_name}'/'{hold_key_name}'")
        Buffer.unregister_event_sequence(tap_key_name)
        for event_sequence, action in [
            (
                f"{tap_key_name}+{str.lower(tap_key_name)}",
                Buffer.clear_after(oneshot(tap_key_name)),
            ),
            (f"@+{tap_key_name}+!", press(hold_key_name)),
            (
                f"_+{tap_key_name}+!",
                Buffer.clear_after(release(hold_key_name)),
            ),
        ]:
            Buffer.register_event_sequence(event_sequence, action)
