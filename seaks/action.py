class Action:
    def __init__(self, callback) -> None:
        self.callback = callback

    def run(self):
        # print("Running action")
        self.callback()