class Buffer:
    instance = None

    def __init__(self) -> None:
        self.content = []
        self.data = ""

    def add_event(self, event_code: str) -> None:
        self.content.append(event_code)
        self.update_data()

    def remove_event(self, event_code: str) -> None:
        self.content.remove(event_code)
        self.update_data()

    def update_data(self) -> None:
        self.data = "/".join(self.content)
        print(self.data)

    @classmethod
    def register(cls, event_id: str) -> None:
        cls.instance.add_event(event_id)

    @classmethod
    def claim(cls, event_id: str) -> None:
        cls.instance.remove_event(event_id)


Buffer.instance = Buffer()
