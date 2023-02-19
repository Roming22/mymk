from time import sleep


class Switch:
    count = 0

    def __init__(self, col, row):
        Switch.count += 1
        self.id = Switch.count
        self.col = col
        self.row = row
        self.is_pressed = False

    def getState(self) -> bool:
        self.is_pressed = False
        return self.is_pressed

    def getEvent(self) -> tuple(int, bool):
        current_state = self.is_pressed
        if current_state != self.getState():
            return (self.id, self.is_pressed)
        return None


class Keyboard:
    def __init__(self, rows: list, cols: list) -> None:
        self.pin_rows = rows
        self.pin_cols = cols
        self.switches = self.__init_switches()

    def __init_switches(self) -> list[Switch]:
        switches = []
        for row in self.pin_rows:
            for col in self.pin_cols:
                switches.append(Switch(col=col, row=row))
        return switches

    def get_events(self):
        while True:
            sleep(2)
            for switch in self.switches:
                print("Reading switch ", switch.id)
                event = switch.getEvent()
                if event:
                    yield event
