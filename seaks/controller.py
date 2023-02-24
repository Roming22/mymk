from seaks.buffer import Buffer
from seaks.event import Event, Timer
from seaks.fps import FPS


class Controller:
    board = None
    tickers = []

    @classmethod
    def set_board(cls, board):
        cls.board = board

    @classmethod
    def register(cls, tickers: "Ticker") -> None:
        print("Adding a Ticker")
        cls.tickers.append(tickers)

    @classmethod
    def run(cls):
        FPS.start(5)
        while True:
            events = Event.get_queue()
            FPS.tick()
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

    def tick(self, _: Event):
        pass
