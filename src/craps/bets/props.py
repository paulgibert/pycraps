from dataclasses import dataclass
from typing import ClassVar, TYPE_CHECKING

from craps.dice import Roll
from craps.bets.model import Bet, BetResult
from craps.exceptions import InsufficientFunds

if TYPE_CHECKING:
    from craps.state import TableState


@dataclass(frozen=True)
class PropBet(Bet):
    """
    Base class for one-roll proposition bets.
    Always ON (works during come-out and point phases).
    """
    is_prop: ClassVar[bool] = True

    def validate(self, state: 'TableState') -> None:
        """Standard validation for all prop bets."""
        if self.stake < 0:
            raise InsufficientFunds("Prop bet amount cannot be negative")
        if self.stake == 0:
            return
        if self.stake > state.bankroll:
            raise InsufficientFunds("Prop bet exceeds bankroll")
        if self.stake < state.prop_min:
            raise InsufficientFunds(f"Prop bet below prop minimum ${state.prop_min}")
        if self.stake > state.table_max:
            raise InsufficientFunds(f"Prop bet exceeds table maximum ${state.table_max}")


@dataclass(frozen=True)
class AnySeven(PropBet):
    """Any 7 - wins on any roll of 7, pays 4:1."""
    increment: ClassVar[tuple[int, ...]] = (1,)

    def settle(self, state: 'TableState', roll: Roll) -> BetResult:
        if self.stake == 0:
            return BetResult(0, 0)
        if roll.total() == 7:
            return BetResult(self.stake + self.stake * 4, 0)  # Pays 4:1
        return BetResult(0, 0)


@dataclass(frozen=True)
class AnyCraps(PropBet):
    """Any Craps - wins on 2, 3, or 12, pays 7:1."""
    increment: ClassVar[tuple[int, ...]] = (1,)

    def settle(self, state: 'TableState', roll: Roll) -> BetResult:
        if self.stake == 0:
            return BetResult(0, 0)
        if roll.total() in (2, 3, 12):
            return BetResult(self.stake + self.stake * 7, 0)  # Pays 7:1
        return BetResult(0, 0)


@dataclass(frozen=True)
class AceDeuce(PropBet):
    """Ace-Deuce (3) - wins on 3, pays 15:1."""
    increment: ClassVar[tuple[int, ...]] = (1,)

    def settle(self, state: 'TableState', roll: Roll) -> BetResult:
        if self.stake == 0:
            return BetResult(0, 0)
        if roll.total() == 3:
            return BetResult(self.stake + self.stake * 15, 0)  # Pays 15:1
        return BetResult(0, 0)


@dataclass(frozen=True)
class Aces(PropBet):
    """Aces (2) - wins on 2, pays 30:1."""
    increment: ClassVar[tuple[int, ...]] = (1,)

    def settle(self, state: 'TableState', roll: Roll) -> BetResult:
        if self.stake == 0:
            return BetResult(0, 0)
        if roll.total() == 2:
            return BetResult(self.stake + self.stake * 30, 0)  # Pays 30:1
        return BetResult(0, 0)


@dataclass(frozen=True)
class Boxcars(PropBet):
    """Boxcars (12) - wins on 12, pays 30:1."""
    increment: ClassVar[tuple[int, ...]] = (1,)

    def settle(self, state: 'TableState', roll: Roll) -> BetResult:
        if self.stake == 0:
            return BetResult(0, 0)
        if roll.total() == 12:
            return BetResult(self.stake + self.stake * 30, 0)  # Pays 30:1
        return BetResult(0, 0)


@dataclass(frozen=True)
class YoLeven(PropBet):
    """Yo-leven (11) - wins on 11, pays 15:1."""
    increment: ClassVar[tuple[int, ...]] = (1,)

    def settle(self, state: 'TableState', roll: Roll) -> BetResult:
        if self.stake == 0:
            return BetResult(0, 0)
        if roll.total() == 11:
            return BetResult(self.stake + self.stake * 15, 0)  # Pays 15:1
        return BetResult(0, 0)


@dataclass(frozen=True)
class Horn(PropBet):
    """
    Horn bet - splits equally on 2, 3, 11, 12.
    Must be divisible by 4.
    Each part pays individually:
    - 2 pays 30:1 on its portion
    - 3 pays 15:1 on its portion
    - 11 pays 15:1 on its portion
    - 12 pays 30:1 on its portion
    """
    increment: ClassVar[tuple[int, ...]] = (4,)

    def settle(self, state: 'TableState', roll: Roll) -> BetResult:
        if self.stake == 0:
            return BetResult(0, 0)

        # Split into 4 equal parts
        part = self.stake // 4
        total = roll.total()

        if total == 2:
            return BetResult(part + part * 30, 0)
        elif total == 3:
            return BetResult(part + part * 15, 0)
        elif total == 11:
            return BetResult(part + part * 15, 0)
        elif total == 12:
            return BetResult(part + part * 30, 0)
        return BetResult(0, 0)

    def validate(self, state: 'TableState') -> None:
        """Validate horn bet - must be divisible by 4."""
        super().validate(state)
        if self.stake > 0 and self.stake % 4 != 0:
            raise InsufficientFunds("Horn bet must be divisible by 4")


@dataclass(frozen=True)
class CAndE(PropBet):
    """
    C&E (Craps and Eleven) - splits equally on Any Craps and 11.
    Must be divisible by 2.
    - Any Craps portion pays 7:1
    - Eleven portion pays 15:1
    """
    increment: ClassVar[tuple[int, ...]] = (2,)

    def settle(self, state: 'TableState', roll: Roll) -> BetResult:
        if self.stake == 0:
            return BetResult(0, 0)

        # Split into 2 equal parts
        part = self.stake // 2
        total = roll.total()

        if total in (2, 3, 12):
            return BetResult(part + part * 7, 0)
        elif total == 11:
            return BetResult(part + part * 15, 0)
        return BetResult(0, 0)

    def validate(self, state: 'TableState') -> None:
        """Validate C&E bet - must be divisible by 2."""
        super().validate(state)
        if self.stake > 0 and self.stake % 2 != 0:
            raise InsufficientFunds("C&E bet must be divisible by 2")
