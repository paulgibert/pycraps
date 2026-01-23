from dataclasses import dataclass

@dataclass(frozen=True)
class BetsMask:
    """
    Contains the valid amounts allowed for each bet type. Each bet always includes 0.
    """
    pass_line: set[int]
