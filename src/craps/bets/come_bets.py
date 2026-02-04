from typing import Optional, Tuple
from craps.phase import TablePhase
from craps.exceptions import IllegalAction
from craps.dice import Roll
from craps.constants import POINTS, NATURAL_WINNERS, CRAPS, SEVEN_OUT
from craps.bets.model import Bet, forbids_target
from craps.bets.utils import TRUE_ODDS


class ComeBets(Bet):
    """Manages all come bets on the table.

    A come bet behaves like a pass line bet but can only be placed after a point
    is established. A pending come bet sits on the come line until the next roll
    resolves it (natural wins, craps loses, or a point number moves it to that
    number). Once moved to a point, odds can be placed behind it. The bet wins
    when that point is rolled again and loses on a seven-out.
    """

    def __init__(self, init_phase: TablePhase):
        super().__init__(init_phase)
        self._pending_stake = 0.0
        self._stake = {n: 0.0 for n in POINTS}
        self._odds = {n: 0.0 for n in POINTS}

    @property
    def is_prop(self) -> bool:
        return False

    def set_stake_targets(self) -> Tuple[Optional[int]]:
        return (None,)
    
    def get_stake_targets(self) -> Tuple[Optional[int]]:
        return (None,) + tuple(POINTS)
    
    def set_odds_targets(self) -> Tuple[Optional[int]]:
        return tuple(POINTS)
    
    def get_odds_targets(self) -> Tuple[Optional[int]]:
        return tuple(POINTS)

    def _settle(self, roll: Roll) -> float:
        """Settle all come bets for the given roll.

        Come-out phase:
            - No action; come bets cannot be active during come-out.

        Point phase:
            - Natural (7, 11): pending come bet wins even money.
            - Craps (2, 3, 12): pending come bet loses.
            - Seven-out (7): all established come bets and odds lose.
            - Point number: pays out any existing come bet on that number at
              true odds, then moves the pending stake to that number.

        Returns:
            The total payout across all come bets, or 0.0 on a loss/no-action.
        """
        total = roll.total()
        if self._phase.point is None:
            return 0.0

        if total == SEVEN_OUT:
            # Pending come bet wins (7 is a natural), but all established
            # come bets and odds are lost.
            winnings = self._pending_stake * 2.0
            self._clear_all()
            return winnings

        if total in NATURAL_WINNERS:
            winnings = self._pending_stake * 2.0
            self._clear_pending()
            return winnings

        if total in CRAPS:
            self._clear_pending()
            return 0.0

        # A point number was rolled
        winnings = (self._stake[total] * 2.0) + (1.0 + TRUE_ODDS[total]) * self._odds[total]
        self._clear_target(total)
        self._move_pending(total)
        return winnings

    @forbids_target
    def _set_stake(self, amount: float, target: Optional[int] = None):
        """Place a come bet (pending).

        Can only be placed during the point phase and must not specify a target.
        The pending stake will be moved to a point number on the next applicable roll.

        Raises:
            IllegalAction: If called during come-out or with a specific target.
        """
        if self._phase.point is None:
            raise IllegalAction("Cannot place a come bet on the come-out roll.")
        self._pending_stake = amount

    def _get_stake(self, target: Optional[int] = None) -> float:
        """Return the current come bet stake.

        Args:
            target: None for the pending stake, or a point number for an
                    established come bet.

        Raises:
            ValueError: If target is not a valid point number.
        """
        if target is None:
            return self._pending_stake
        if target not in POINTS:
            raise ValueError(f"'target' must be one of: {POINTS}. Got: {target}")
        return self._stake[target]

    def _set_odds(self, amount: float, target: Optional[int] = None):
        """Set odds behind an established come bet.

        Requires a specific point target that has an existing come bet stake.

        Raises:
            IllegalAction: If target is None or no come bet exists on the target.
        """
        if target is None:
            raise IllegalAction("Cannot set odds without a target.")
        if target not in POINTS:
            raise ValueError(f"'target' must be one of: {POINTS}. Got: {target}")
        if self._stake[target] == 0:
            raise IllegalAction(f"No come bet on {target}.")
        self._odds[target] = amount

    def _get_odds(self, target: Optional[int] = None) -> float:
        """Return the current odds amount for a come point.

        Raises:
            IllegalAction: If target is None.
            ValueError: If target is not a valid point number.
        """
        if target is None:
            raise IllegalAction("Cannot get odds without a target.")
        if target not in POINTS:
            raise ValueError(f"'target' must be one of: {POINTS}. Got: {target}")
        return self._odds[target]

    def _clear_pending(self):
        """Reset the pending come bet stake to zero."""
        self._pending_stake = 0.0

    def _clear_target(self, target: int):
        """Reset stake and odds for a specific come point."""
        if target not in POINTS:
            raise ValueError(f"Tried to clear come bets on invalid target: {target}")
        self._stake[target] = 0.0
        self._odds[target] = 0.0

    def _clear_all(self):
        """Reset all come bets, odds, and pending stake."""
        for target in POINTS:
            self._clear_target(target)
        self._clear_pending()

    def _move_pending(self, target: int):
        """Move the pending come bet to an established come point."""
        if target not in POINTS:
            raise ValueError(f"Tried to move come pending to an invalid target: {target}")
        self._stake[target] = self._pending_stake
        self._clear_pending()
