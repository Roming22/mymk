class State:
    def __init__(self, name) -> None:
        self.name = name
        self.events = list()

    def process_event(self, event) -> None:
        if (event.object, event.value) in self.events:
            print(f"{self.name} is processing ({(event.object, event.value)})")
        else:
            print(f"{self.name} is ignoring ({(event.object, event.value)})")


class StateMachine:
    machines = list()

    def __init__(self, name) -> None:
        self.name = name
        self.states = dict()
        self._active_state = None
        StateMachine.machines.append(self)

    def add_state(self, state) -> None:
        # print("StateMachine: Adding state", state.name)
        self.states[state.name] = state
        if self._active_state is None:
            self.active_state(state.name)

    def active_state(self, state_name) -> None:
        # print("StateMachine: Activating state", state_name)
        self._active_state = self.states[state_name]

    def process_event(self, event) -> None:
        self._active_state.process_event(event)

    @classmethod
    def register_event(cls, event):
        for sm in cls.machines:
            sm.process_event(event)