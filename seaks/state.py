from seaks.controller import Ticker
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


class StateMachine(Ticker):
    def __init__(self, name: str, state_names: list[str]) -> None:
        self.name = name
        self.states = dict()
        for name in state_names:
            self.add_state(name)
        self._active_state = self.states[state_names[0]]
        self.register()

    def __getitem__(self, key):
        return self.states[key]

    def add_state(self, state_name: str) -> State:
        state = State(f"{state_name}", self)
        # print("StateMachine: Adding state", state.name)
        self.states[state_name] = state
        return state

    def activate_state(self, state: State) -> None:
        print(f"    Activating {state.fullname}")
        Trigger(f"{self._active_state.fullname}", False).fire()
        Trigger(f"{state.fullname}", True).fire()
        self._active_state = state

    def tick(self, event) -> None:
        self._active_state.process_event(event)
