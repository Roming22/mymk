from seaks.logic.event import Event, Timer


class Controller:
    board = None
    tickers: list["Ticker"] = []

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
        for event in Event.get_next():
            for ticker in cls.tickers:
                ticker.tick(event)


class Ticker:
    """
    Tickers generate and/or process events at each tick
    """

    def register(self) -> None:
        Controller.register(self)

    def unregister(self) -> None:
        Controller.unregister(self)

    def tick(self, _: Event = None) -> None:
        pass
