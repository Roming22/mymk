from mymk.hardware.keys import press, release


class Key:
    @staticmethod
    def load(switch_uid: str, keycode: str, universe) -> None:
        timelines_events = []
        if keycode in ["NO", None]:
            return timelines_events
        timelines_events.append(
            [
                (switch_uid, universe.mark_determined, lambda: press(keycode)),
                (f"!{switch_uid}", None, lambda: release(keycode)),
            ]
        )
        return timelines_events
