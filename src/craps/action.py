from dataclasses import dataclass
from craps.bets.model import Bets

@dataclass(frozen=True)
class Action:
    """
    Action to be taken by the player.

    The bets field represents the absolute bet state to set on the table.
    The leave field indicates whether the player is leaving the table.
    Note: When leaving, bets will still update the table state and bankroll.
    """
    bets: Bets
    leave: bool = False
