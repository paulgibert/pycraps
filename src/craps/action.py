from dataclasses import dataclass
from craps.bets.model import ActionBets

@dataclass(frozen=True)
class Action:
    """
    Action to be taken by the player.

    The bets field contains only player-controllable bets.
    The leave field indicates whether the player is leaving the table.
    Note: When leaving, bets will still update the table state and bankroll.
    """
    bets: ActionBets
    leave: bool = False
