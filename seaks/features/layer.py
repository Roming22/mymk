from seaks.state import StateMachine


class Layer(StateMachine):
    def __init__(self, state_names: list[str], name: str = "layer") -> None:
        super().__init__(name, state_names)
