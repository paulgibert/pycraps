from dataclasses import dataclass, replace, fields
from typing import Iterator

@dataclass(frozen=True)
class Bets:
    """
    Represents all bet amounts on the table.
    """
    pass_line: int = 0
    pass_odds: int = 0
    # dont_pass: int

    # dont_pass_odds: int

    # come: Dict[int, int]          # keyed by number
    # dont_come: Dict[int, int]

    # come_odds: Dict[int, int]
    # dont_come_odds: Dict[int, int]

    # place: Dict[int, int]         # 4,5,6,8,9,10
    # buy: Dict[int, int]
    # lay: Dict[int, int]

    # field: int
    # hardways: Dict[int, int]      # 4,6,8,10
    # props: Dict[str, int]

def set_bets(bets: Bets, slot: str, stake: int) -> Bets:
    """
    Returns a new Bets object with the specified bet slot set to the given stake.
    Auto-scales with Bets dataclass fields.
    """
    if not hasattr(bets, slot):
        raise KeyError(f"Unknown bet slot: {slot}")
    return replace(bets, **{slot: stake})

def iter_bets(bets: Bets) -> Iterator[tuple[str, int]]:
    """
    Iterates over bet slots and their stakes.
    Auto-scales with Bets dataclass fields.
    """
    for field in fields(Bets):
        yield (field.name, getattr(bets, field.name))
