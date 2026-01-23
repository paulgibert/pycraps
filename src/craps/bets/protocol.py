from typing import Protocol
from dataclasses import dataclass
from craps.state import TableState
from craps.dice import Roll

@dataclass(frozen=True)
class BetResult:
    """
    The result of a settled bet.

    bankroll_delta: Amount to add to the bankroll (includes winnings minus losses).
    remaining_stake: Amount of the wager that remains on the table after settlement.
                     For pass line bets this is zero (bet is resolved).
                     For place bets this would be the original stake (bet rides on a win).
    """
    bankroll_delta: int
    remaining_stake: int

class BetType(Protocol):
    """
    Protocol for all bet types on the table.
    """
    def settle(
        self,
        state: TableState,
        stake: int,
        roll: Roll
    ) -> BetResult:
        """
        Determines the outcome of a bet based on the roll and table state.

        Returns a BetResult indicating bankroll changes and remaining stake.
        Does not modify the table state.
        """
        pass

    def validate(
        self,
        state: TableState,
        stake: int
    ) -> None:
        """
        Validates that the target stake is legal given the current state.

        Raises IllegalAction if the bet is invalid.
        """
        pass
