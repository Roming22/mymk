def pretty_print(timestamp: int):
    useconds = timestamp % 10**9 // 1000
    seconds = (timestamp // 10**9) % 60
    minutes = ((timestamp // 10**9) // 60) % 60
    hours = (timestamp // 10**9) // 3600 % 24
    days = (timestamp // 10**9) // (3600 * 24)
    return f"{days:03d} days, {hours:02d}:{minutes:02d}:{seconds:02d}.{useconds:06d}"
