from seaks.buffer import Buffer
from seaks.event import Event, Timer


class Controller:
    board = None
    tickers = []

    @classmethod
    def set_board(cls, board):
        cls.board = board

    @classmethod
    def register(cls, ticker: "Ticker") -> None:
        print("Adding a Ticker")
        cls.tickers.append(ticker)

    @classmethod
    def unregister(cls, ticker: "Ticker") -> None:
        print("Removing a Ticker")
        cls.tickers.remove(ticker)

    @classmethod
    def run(cls):
        events = Event.get_queue()
        cls.board.tick()
        Timer.tick()
        for event in events:
            print(event)
            for ticker in cls.tickers:
                ticker.tick(event)
        Buffer.flush()


class Ticker:
    """
    Tickers generate events at each tick
    """

    def register(self):
        Controller.register(self)

    def unregister(self):
        Controller.unregister(self)

    def tick(self, _: Event):
        pass
