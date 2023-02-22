from seaks.event import Event, Trigger


class State:
    def __init__(self, name: str, machine: "StateMachine") -> None:
        self.name = name
        self.machine = machine
        self.fullname = f"{self.machine.name}.{self.name}"
        self.triggers = dict()

    def add_trigger(self, trigger: Trigger, action):
        self.triggers[trigger] = action

    def process_event(self, event: Event) -> None:
        if action := self.triggers.get(event.trigger, None):
            print(f"  {self.fullname} is processing the event")
            action.run()
        # else:
        #     print(f"  {self.fullname} is ignoring the event")


class StateMachine:
    machines = list()

    def __init__(self, name: str) -> None:
        self.name = name
        self.states = dict()
        self._active_state = State("None", self)
        StateMachine.machines.append(self)

    def new_state(self, state_name: str) -> State:
        state = State(f"{state_name}", self)
        # print("StateMachine: Adding state", state.name)
        self.states[state_name] = state
        return state

    def activate_state(self, state: State) -> None:
        print(f"    Activating {state.fullname}")
        Trigger(f"{self._active_state.fullname}", False).fire()
        Trigger(f"{state.fullname}", True).fire()
        self._active_state = state

    @classmethod
    def process_events(cls) -> None:
        if event := Event.get_next():
            print(event)
            for sm in cls.machines:
                sm.process_event(event)

    def process_event(self, event) -> None:
        state = self._active_state.process_event(event)
