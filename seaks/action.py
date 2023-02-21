class Action:
    noop = None

    def __init__(self, callback) -> None:
        self.callback = callback

    def run(self):
        # print("Running action")
        self.callback()


def noop():
    return True


Action.noop = Action(noop)
