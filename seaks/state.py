class State:
    def __init__(self, name) -> None:
        self.name = name
        self.triggers = dict()

    def add_trigger(self, trigger, action, state):
        self.triggers[trigger] = (action, state)

    def process_event(self, event) -> State:
        action, state = self.triggers.get(event.trigger, (None, None))
        if action:
            print(f"{self.name} is processing ({event.trigger})")
            action.run()
            return state
        else:
            print(f"{self.name} is ignoring ({event.trigger})")
            return self


class StateMachine:
    machines = list()

    def __init__(self, name) -> None:
        self.name = name
        self.states = dict()
        self._active_state = None
        StateMachine.machines.append(self)

    def new_state(self, state_name) -> State:
        state = State(state_name)
        # print("StateMachine: Adding state", state.name)
        self.states[state.name] = state
        if self._active_state is None:
            self.activate_state(state)
        return state

    def activate_state(self, state) -> None:
        print("# StateMachine: Activating state", state.name)
        self._active_state = state

    def process_event(self, event) -> None:
        state = self._active_state.process_event(event)
        if self._active_state != state:
            self.activate_state(state)

    @classmethod
    def register_event(cls, event):
        for sm in cls.machines:
            sm.process_event(event)