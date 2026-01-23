from dataclasses import dataclass
from typing import Optional
from craps.bets.model import Bets
from craps.dice import Roll

@dataclass(frozen=True)
class TableState:
    """
    Represents the current state of the table including bets and phase state.
    """
    bankroll: int
    roll_count: int
    point: Optional[int]
    bets: Bets
    last_roll: Optional[Roll]
    is_terminal: bool
    table_min: int
    table_max: int
