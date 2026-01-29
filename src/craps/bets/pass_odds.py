from dataclasses import dataclass
from typing import ClassVar, TYPE_CHECKING

from craps.dice import Roll
from craps.bets.model import Bet, BetResult
from craps.exceptions import InsufficientFunds

if TYPE_CHECKING:
    from craps.state import TableState


@dataclass(frozen=True)
class PassOdds(Bet):
    """
    Pass line odds bet. Pays true odds based on point.
    Only valid when point is established and pass line bet exists.
    """
    increment: ClassVar[tuple[int, ...]] = (1, 2, 5)  # depends on point: 4/10=1, 5/9=2, 6/8=5
    is_odds: ClassVar[bool] = True

    def settle(self, state: 'TableState', roll: Roll) -> BetResult:
        if self.stake == 0 or state.point is None:
            return BetResult(0, self.stake)

        if roll.total() == state.point:
            winnings = self._calculate_winnings(state.point)
            return BetResult(self.stake + winnings, 0)
        elif roll.total() == 7:
            return BetResult(0, 0)
        else:
            return BetResult(0, self.stake)

    def _calculate_winnings(self, point: int) -> int:
        """True odds: 4/10 pays 2:1, 5/9 pays 3:2, 6/8 pays 6:5."""
        if point in (4, 10):
            return self.stake * 2
        elif point in (5, 9):
            return self.stake * 3 // 2
        elif point in (6, 8):
            return self.stake * 6 // 5
        return 0

    def validate(self, state: 'TableState') -> None:
        if self.stake < 0:
            raise InsufficientFunds("Bet amount cannot be negative")
        if self.stake == 0:
            return
        if state.point is None:
            raise InsufficientFunds("Cannot place odds bet without point established")
        if state.bets.pass_line.stake == 0:
            raise InsufficientFunds("Must have pass line bet to place odds")
        if self.stake > state.bankroll:
            raise InsufficientFunds("Bet exceeds bankroll")
        max_odds = state.bets.pass_line.stake * state.max_odds
        if self.stake > max_odds:
            raise InsufficientFunds(f"Odds bet cannot exceed {state.max_odds}x pass line bet")
        # Increment rules for clean payouts
        if state.point in (5, 9):
            if self.stake % 2 != 0:
                raise InsufficientFunds("Odds on point 5/9 must be even amounts")
        elif state.point in (6, 8):
            if self.stake % 5 != 0:
                raise InsufficientFunds("Odds on point 6/8 must be multiples of $5")
