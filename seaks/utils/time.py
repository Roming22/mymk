import time


def pretty_print(timestamp: int):
    useconds = timestamp % 10**9 // 1000
    seconds = (timestamp // 10**9) % 60
    minutes = ((timestamp // 10**9) // 60) % 60
    hours = (timestamp // 10**9) // 3600 % 24
    days = (timestamp // 10**9) // (3600 * 24)
    return f"{days:03d} days, {hours:02d}:{minutes:02d}:{seconds:02d}.{useconds:06d}"


def time_it(func):
    def wrapper(*args, **kwargs):
        now = time.monotonic_ns()
        result = func(*args, **kwargs)
        print(
            " ".join(["#", str((time.monotonic_ns() - now) / 10**6), "#" * 120])[:120]
        )
        return result

    return wrapper
