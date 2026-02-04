from typing import Optional, Tuple
from craps.phase import TablePhase
from craps.dice import Roll
from craps.constants import NATURAL_WINNERS, CRAPS, SEVEN_OUT, POINTS
from craps.bets.model import Bet, forbids_target, requires_target
from craps.bets.utils import TRUE_ODDS, TRUE_ODDS_INCREMENT
from craps.exceptions import IllegalAction


class PassLine(Bet):
    """A pass line bet in craps.

    During the come-out phase, a natural (7 or 11) wins even money and craps
    (2, 3, or 12) loses. Any other roll establishes the point. Once a point is
    established, hitting the point wins and a seven-out loses. Odds bets can be
    placed behind the pass line after a point is established, paying at true odds.
    """

    def __init__(self, init_phase: TablePhase):
        super().__init__(init_phase)
        self._stake = 0
        self._odds = 0

    @property
    def is_prop(self) -> bool:
        return False

    def set_stake_targets(self) -> Tuple[Optional[int]]:
        return (None,)
    
    def get_stake_targets(self) -> Tuple[Optional[int]]:
        return (None,)
    
    def set_odds_targets(self) -> Tuple[Optional[int]]:
        return (None,)
    
    def get_odds_targets(self) -> Tuple[Optional[int]]:
        return (None,)

    @forbids_target
    def get_stake_increment(self, target: Optional[int] = None) -> int:
        return 1

    @requires_target(POINTS)
    def get_odds_increment(self, target: Optional[int] = None) -> Optional[int]:
        return TRUE_ODDS_INCREMENT[target]

    def _settle(self, roll: Roll) -> float:
        """Settle the pass line bet for the given roll.

        Come-out phase:
            - Natural (7, 11): pays 2x stake.
            - Craps (2, 3, 12): loses stake.
            - Any other total: no action (point is established elsewhere).

        Point phase:
            - Rolling the point: pays 2x stake plus odds at true odds.
            - Seven-out: loses both stake and odds.
            - Any other total: no action.

        Returns:
            The total payout (stake return + winnings), or 0.0 on a loss/no-action.
        """
        total = roll.total()
        if self._phase.point is None:
            if total in NATURAL_WINNERS:
                winnings = self._stake * 2
                self._clear()
                return winnings
            elif total in CRAPS:
                self._clear()
                return 0.0
            return 0.0

        if total == SEVEN_OUT:
            self._clear()
            return 0.0

        if total == self._phase.point:
            winnings = (self._stake * 2) + (1.0 + TRUE_ODDS[total]) * self._odds
            self._clear()
            return winnings

        return 0.0

    @forbids_target
    def _set_stake(self, amount: float, target: Optional[None] = None):
        """Set the flat pass line wager.

        Can only be set during the come-out phase. Once a point is established
        the stake is locked until the bet resolves.

        Raises:
            IllegalAction: If a point is already established.
        """
        if self._phase.point is not None:
            raise IllegalAction("Cannot set stake during point phase.")
        self._stake = amount

    @forbids_target
    def _get_stake(self, target: Optional[None] = None) -> float:
        """Return the current flat pass line wager."""
        return self._stake

    @forbids_target
    def _set_odds(self, amount: float, target: Optional[None] = None):
        """Set the odds bet behind the pass line.

        Odds can only be placed after a point is established and require an
        existing flat stake. Calling this again replaces the previous odds amount.

        Raises:
            IllegalAction: If no point is established or no flat stake exists.
        """
        if self._phase.point is None:
            raise IllegalAction("Cannot set odds during come-out phase.")
        if self._stake == 0:
            raise IllegalAction("Cannot set odds without a pass line stake.")
        self._odds = amount

    @forbids_target
    def _get_odds(self, target: Optional[None] = None) -> float:
        """Return the current odds bet amount."""
        return self._odds

    def _clear(self):
        """Reset stake and odds to zero after the bet resolves."""
        self._stake = 0
        self._odds = 0
