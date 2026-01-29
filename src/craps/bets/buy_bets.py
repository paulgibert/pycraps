import math
from dataclasses import dataclass
from typing import ClassVar, TYPE_CHECKING

from craps.dice import Roll
from craps.bets.model import Bet, BetResult
from craps.exceptions import InsufficientFunds

if TYPE_CHECKING:
    from craps.state import TableState


@dataclass(frozen=True)
class BuyBet(Bet):
    """
    Base class for buy bets. Like place bets but pay true odds minus 5% commission.
    OFF during come-out, wins on number, loses on 7.
    """
    number: ClassVar[int]

    def settle(self, state: 'TableState', roll: Roll) -> BetResult:
        if self.stake == 0:
            return BetResult(0, 0)
        # OFF during come-out
        if state.point is None:
            return BetResult(0, self.stake)
        if roll.total() == self.number:
            winnings = self._calculate_winnings()
            return BetResult(winnings, self.stake)  # Bet stays on table
        elif roll.total() == 7:
            return BetResult(0, 0)
        else:
            return BetResult(0, self.stake)

    def _calculate_winnings(self) -> int:
        """True odds minus 5% commission: 2:1 for 4/10, 3:2 for 5/9, 6:5 for 6/8."""
        if self.number in (4, 10):
            gross = self.stake * 2
        elif self.number in (5, 9):
            gross = self.stake * 3 // 2
        elif self.number in (6, 8):
            gross = self.stake * 6 // 5
        else:
            return 0
        commission = math.ceil(self.stake * 0.05)
        return gross - commission

    def validate(self, state: 'TableState') -> None:
        if self.stake < 0:
            raise InsufficientFunds("Buy bet cannot be negative")
        if self.stake == 0:
            return
        if self.stake > state.bankroll:
            raise InsufficientFunds("Buy bet exceeds bankroll")
        if self.stake < state.table_min:
            raise InsufficientFunds(f"Buy bet below table minimum ${state.table_min}")
        if self.stake > state.table_max:
            raise InsufficientFunds(f"Buy bet exceeds table maximum ${state.table_max}")
        # Increment validation for clean payouts
        if self.number in (5, 9) and self.stake % 2 != 0:
            raise InsufficientFunds(f"Buy bet on {self.number} must be even amounts for 3:2 payout")
        elif self.number in (6, 8) and self.stake % 5 != 0:
            raise InsufficientFunds(f"Buy bet on {self.number} must be multiples of $5 for 6:5 payout")


@dataclass(frozen=True)
class Buy4(BuyBet):
    number: ClassVar[int] = 4
    increment: ClassVar[tuple[int, ...]] = (1,)


@dataclass(frozen=True)
class Buy5(BuyBet):
    number: ClassVar[int] = 5
    increment: ClassVar[tuple[int, ...]] = (2,)


@dataclass(frozen=True)
class Buy6(BuyBet):
    number: ClassVar[int] = 6
    increment: ClassVar[tuple[int, ...]] = (5,)


@dataclass(frozen=True)
class Buy8(BuyBet):
    number: ClassVar[int] = 8
    increment: ClassVar[tuple[int, ...]] = (5,)


@dataclass(frozen=True)
class Buy9(BuyBet):
    number: ClassVar[int] = 9
    increment: ClassVar[tuple[int, ...]] = (2,)


@dataclass(frozen=True)
class Buy10(BuyBet):
    number: ClassVar[int] = 10
    increment: ClassVar[tuple[int, ...]] = (1,)
