def hash(string: str) -> int:
    bits = "".join([f"{bin(ord(c))}"[2:] for c in string])
    value = int(bits, 2) % 10**9
    return value


def permutations(items: list) -> list[list]:
    if len(items) <= 1:
        return [items]

    result = []
    for i in range(len(items)):
        # Take the current element as the first element
        first = items[i]

        # Generate permutations of the remaining elements
        remaining = items[:i] + items[i + 1 :]
        sub_permutations = permutations(remaining)

        # Append the first element to each permutation
        for perm in sub_permutations:
            result.append([first] + perm)

    return result
