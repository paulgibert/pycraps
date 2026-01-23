from dataclasses import dataclass, replace
from typing import Iterator

@dataclass(frozen=True)
class Bets:
    """
    Represents all bet amounts on the table.
    """
    pass_line: int
    # dont_pass: int

    # pass_odds: int
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
    """
    if slot == 'pass_line':
        return replace(bets, pass_line=stake)
    raise KeyError(f"Unknown bet slot: {slot}")

def iter_bets(bets: Bets) -> Iterator[tuple[str, int]]:
    """
    Iterates over bet slots and their stakes.
    """
    yield ('pass_line', bets.pass_line)
