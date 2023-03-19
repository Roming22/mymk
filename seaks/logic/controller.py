from seaks.logic.buffer import Buffer
from seaks.logic.event import Timer


class Controller:
    board = None
    tickers: list["Ticker"] = []
    state = ""

    @classmethod
    def set_board(cls, board) -> None:
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
    def run(cls) -> None:
        if cls.board is not None:
            cls.board.tick()
        Timer.tick()
        # print(end=".")
        if cls.state != Buffer.instance.data:
            for ticker in cls.tickers:
                print(type(ticker))
                ticker.tick()
            cls.state = Buffer.instance.data


class Ticker:
    """
    Tickers generate and/or process events at each tick
    """

    def register(self) -> None:
        Controller.register(self)

    def unregister(self) -> None:
        Controller.unregister(self)

    def tick(self) -> None:
        pass
