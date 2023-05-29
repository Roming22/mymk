def chain(*actions: callable) -> callable:
    func = lambda: [action() for action in actions]
    return func
