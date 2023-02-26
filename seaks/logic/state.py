from seaks.logic.action import Action
from seaks.logic.controller import Ticker
from seaks.logic.event import Event, Trigger


class State:
    def __init__(self, name: str, machine: "StateMachine") -> None:
        self.name = name
        self.machine = machine
        self.fullname = f"{self.machine.name}.{self.name}"
        self.triggers: dict[Trigger, Action] = dict()

    def add_trigger(self, trigger: Trigger, action):
        print(
            f"    Adding ({trigger.object},{trigger.value}) to {self.fullname} triggers."
        )
        self.triggers[trigger] = action

    def process_event(self, event: Event) -> None:
        if action := self.triggers.get(event.trigger, None):
            # print(
            #     f"    {self.fullname} has an action for ({event.trigger.object}, {event.trigger.value})"
            # )
            action.run()
        # else:
        #     print(f"  {self.fullname} is ignoring the event")


class StateMachine(Ticker):
    machines: dict[str, "StateMachine"] = dict()

    def __init__(
        self,
        name: str,
        state_names: list[str],
    ) -> None:
        print(f"StateMachine {name}: {state_names}")
        StateMachine.machines[name] = self
        self.name = name
        self.states: dict[str, State] = dict()
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
        self._active_state = state
        self.start()

    def start(self):
        state = self._active_state
        print(f"    Activating {state.fullname}")

    def tick(self, event: Event = None) -> None:
        self._active_state.process_event(event)