from collections import namedtuple

Switch = namedtuple("Switch", ["name", "id"])


def instanciate_matrix(name: str, row_count: int, col_count: int) -> list["Switch"]:
    matrix: list["Switch"] = []
    for row in range(0, row_count):
        for col in range(0, col_count):
            switch_id = row * col_count + col
            name = f"switch.{switch_id}"
            matrix.append(Switch(name, switch_id))
    return matrix
