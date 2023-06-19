import time


class Time:
    tick_time = 0

    @classmethod
    def tick(cls) -> None:
        cls.tick_time = cls.now()

    @staticmethod
    def now() -> int:
        return time.monotonic_ns()


Time.tick_time = Time.now()


def pretty_print(timestamp: int) -> None:
    useconds = timestamp % 10**9 // 1000
    seconds = (timestamp // 10**9) % 60
    minutes = ((timestamp // 10**9) // 60) % 60
    hours = (timestamp // 10**9) // 3600 % 24
    days = (timestamp // 10**9) // (3600 * 24)
    return f"{days:03d} days, {hours:02d}:{minutes:02d}:{seconds:02d}.{useconds:06d}"


def time_it(func):
    def wrapper(*args, **kwargs):
        now = Time.now()
        result = func(*args, **kwargs)
        print(" ".join(["#", str((Time.now() - now) / 10**6), "#" * 120])[:120])
        return result

    return wrapper
