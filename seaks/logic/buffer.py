class Buffer:
    instance = None

    def __init__(self) -> None:
        self.content = []

    def add_event(self, event_code):
        self.content.append(event_code)

    @classmethod
    def register(cls, switch_id):
        cls.instance.add_event(switch_id)
        print("/".join(cls.instance.content))

Buffer.instance = Buffer()
