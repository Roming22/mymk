def hash(string: str) -> int:
    bits = "".join([f"{bin(ord(c))}"[2:] for c in string])
    value = int(bits, 2) % 10**9
    return value


def permutations(items: list, n=None):
    if n is None:
        n = len(items)
    if n == 1:
        yield items
    else:
        for i in range(n - 1):
            for permutation in permutations(items, n - 1):
                yield permutation
            j = 0 if (n % 2) == 1 else i
            items[j], items[n - 1] = items[n - 1], items[j]
        for permutation in permutations(items, n - 1):
            yield permutation
