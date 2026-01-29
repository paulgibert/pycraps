from dataclasses import dataclass
from typing import ClassVar, TYPE_CHECKING

from craps.dice import Roll
from craps.bets.model import Bet, BetResult
from craps.exceptions import InsufficientFunds

if TYPE_CHECKING:
    from craps.state import TableState


@dataclass(frozen=True)
class PlaceBet(Bet):
    """
    Base class for place bets. OFF during come-out, wins on number, loses on 7.
    Subclasses set the specific number and increment.
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
        """9:5 for 4/10, 7:5 for 5/9, 7:6 for 6/8."""
        if self.number in (4, 10):
            return self.stake * 9 // 5
        elif self.number in (5, 9):
            return self.stake * 7 // 5
        elif self.number in (6, 8):
            return self.stake * 7 // 6
        return 0

    def validate(self, state: 'TableState') -> None:
        if self.stake < 0:
            raise InsufficientFunds("Place bet cannot be negative")
        if self.stake == 0:
            return
        if self.stake > state.bankroll:
            raise InsufficientFunds("Place bet exceeds bankroll")
        if self.stake < state.table_min:
            raise InsufficientFunds(f"Place bet below table minimum ${state.table_min}")
        if self.stake > state.table_max:
            raise InsufficientFunds(f"Place bet exceeds table maximum ${state.table_max}")
        # Increment validation
        incr = self.increment[0]
        if self.stake % incr != 0:
            raise InsufficientFunds(f"Place bet on {self.number} must be multiples of ${incr}")


@dataclass(frozen=True)
class Place4(PlaceBet):
    number: ClassVar[int] = 4
    increment: ClassVar[tuple[int, ...]] = (5,)


@dataclass(frozen=True)
class Place5(PlaceBet):
    number: ClassVar[int] = 5
    increment: ClassVar[tuple[int, ...]] = (5,)


@dataclass(frozen=True)
class Place6(PlaceBet):
    number: ClassVar[int] = 6
    increment: ClassVar[tuple[int, ...]] = (6,)


@dataclass(frozen=True)
class Place8(PlaceBet):
    number: ClassVar[int] = 8
    increment: ClassVar[tuple[int, ...]] = (6,)


@dataclass(frozen=True)
class Place9(PlaceBet):
    number: ClassVar[int] = 9
    increment: ClassVar[tuple[int, ...]] = (5,)


@dataclass(frozen=True)
class Place10(PlaceBet):
    number: ClassVar[int] = 10
    increment: ClassVar[tuple[int, ...]] = (5,)
