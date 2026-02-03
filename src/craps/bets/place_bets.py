from typing import Optional
from craps.phase import TablePhase
from craps.exceptions import IllegalAction
from craps.dice import Roll
from craps.constants import POINTS, NATURAL_WINNERS, CRAPS, SEVEN_OUT
from craps.bets.model import Bet, requires_target, forbids_odds__do_not_call
from craps.bets.utils import TRUE_ODDS

PLACE_ODDS = {
    4: 9/5,
    5: 7/5,
    6: 7/6,
    8: 7/6,
    9: 7/5,
    10: 9/5
}

class PlaceBets(Bet):
    """Place bets on specific point numbers (4, 5, 6, 8, 9, 10)."""

    def __init__(self, init_phase: TablePhase):
        super().__init__(init_phase)
        self._stake = {n: 0.0 for n in POINTS}

    def _settle(self, roll: Roll) -> float:
        """Settle place bets based on the roll. Off on come-out, lost on seven-out."""
        total = roll.total()
        if self._phase.point is None:
            # Note: Place bets are off on come-out
            return 0.0

        if total == SEVEN_OUT:
            self._clear_all()
            return 0.0

        if total in POINTS:
            # Note: After a win the original stake remains
            return self._stake[total] * PLACE_ODDS[total]

        return 0.0

    @requires_target(POINTS)
    def _set_stake(self, amount: float, target: Optional[int] = None):
        """Set the stake for a specific point number."""
        if self._phase.point is None:
            raise IllegalAction(f"Cannot adjust place bets on the come-out.")
        self._stake[target] = amount

    @requires_target(POINTS)
    def _get_stake(self, target: Optional[int] = None) -> float:
        """Get the stake for a specific point number."""
        return self._stake[target]

    @forbids_odds__do_not_call
    def _set_odds(self, amount: float, target: Optional[int] = None):
        pass
    
    @forbids_odds__do_not_call
    def _get_odds(self, target: Optional[int] = None) -> float:
        pass

    def _clear_all(self):
        """Clear the state on all place bets."""
        for target in POINTS:
            self._stake[target] = 0.0
