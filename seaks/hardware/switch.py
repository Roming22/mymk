from seaks.utils.memory import memory_cost


class Switch:
    matrix: dict[str, list["Switch"]] = {}

    @memory_cost("Switch")
    def __init__(self, name: str, id: str) -> None:
        self.name = f"switch.{id}"
        self.id = id
        # This might become handy in the future.
        # The naming convention might make it unnecessary.
        # self.fullname = f"switch.{name}_{id:03d}]"

    @classmethod
    def instanciate_matrix(
        cls, name: str, row_count: int, col_count: int, get_id
    ) -> list["Switch"]:
        matrix: list["Switch"] = []
        for row in range(0, row_count):
            for col in range(0, col_count):
                switch_id = get_id(row * col_count + col)
                matrix.append(cls(name, switch_id))
        cls.matrix[name] = matrix
        return matrix
