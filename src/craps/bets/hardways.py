from dataclasses import dataclass
from typing import ClassVar, TYPE_CHECKING

from craps.dice import Roll
from craps.bets.model import Bet, BetResult
from craps.exceptions import InsufficientFunds

if TYPE_CHECKING:
    from craps.state import TableState


@dataclass(frozen=True)
class HardwayBet(Bet):
    """
    Base class for hardway bets. Wins on doubles, loses on easy or 7.
    OFF during come-out. Hard 4/10 pays 7:1, Hard 6/8 pays 9:1.
    """
    number: ClassVar[int]

    def settle(self, state: 'TableState', roll: Roll) -> BetResult:
        if self.stake == 0:
            return BetResult(0, 0)
        # OFF during come-out
        if state.point is None:
            return BetResult(0, self.stake)
        # Win if rolled the hard way (doubles)
        if roll.total() == self.number and roll[0] == roll[1]:
            if self.number in (4, 10):
                return BetResult(self.stake + self.stake * 7, 0)  # 7:1
            else:  # 6, 8
                return BetResult(self.stake + self.stake * 9, 0)  # 9:1
        # Lose if rolled easy or 7
        elif roll.total() == self.number or roll.total() == 7:
            return BetResult(0, 0)
        else:
            return BetResult(0, self.stake)

    def validate(self, state: 'TableState') -> None:
        if self.stake < 0:
            raise InsufficientFunds("Hardway bet cannot be negative")
        if self.stake == 0:
            return
        if self.stake > state.bankroll:
            raise InsufficientFunds("Hardway bet exceeds bankroll")
        if self.stake < state.prop_min:
            raise InsufficientFunds(f"Hardway bet below prop minimum ${state.prop_min}")
        if self.stake > state.table_max:
            raise InsufficientFunds(f"Hardway bet exceeds table maximum ${state.table_max}")


@dataclass(frozen=True)
class Hard4(HardwayBet):
    number: ClassVar[int] = 4
    increment: ClassVar[tuple[int, ...]] = (1,)


@dataclass(frozen=True)
class Hard6(HardwayBet):
    number: ClassVar[int] = 6
    increment: ClassVar[tuple[int, ...]] = (1,)


@dataclass(frozen=True)
class Hard8(HardwayBet):
    number: ClassVar[int] = 8
    increment: ClassVar[tuple[int, ...]] = (1,)


@dataclass(frozen=True)
class Hard10(HardwayBet):
    number: ClassVar[int] = 10
    increment: ClassVar[tuple[int, ...]] = (1,)
