from craps.bets.protocol import BetType, BetResult
from craps.state import TableState
from craps.dice import Roll
from craps.exceptions import IllegalAction


class PlaceBet(BetType):
    """
    Place bet on a specific number (4, 5, 6, 8, 9, 10).

    Rules:
    - OFF during come-out roll (no action when state.point is None)
    - Wins when the number is rolled (stays on table after win)
    - Loses on seven-out
    - Pays true casino odds: 9:5 for 4/10, 7:5 for 5/9, 7:6 for 6/8
    - Increment requirements: 6/8 multiples of $6, 5/9 multiples of $5, 4/10 multiples of $5
    """

    def __init__(self, number: int):
        if number not in (4, 5, 6, 8, 9, 10):
            raise ValueError(f"Invalid place number: {number}")
        self.number = number

    def settle(self, state: TableState, stake: int, roll: Roll) -> BetResult:
        """Settle place bet for a given roll."""
        if stake == 0:
            return BetResult(0, 0)

        # OFF during come-out roll
        if state.point is None:
            return BetResult(0, stake)

        # Win if number is rolled
        if roll.total() == self.number:
            winnings = self._calculate_winnings(stake)
            return BetResult(stake + winnings, stake)  # Stay on table

        # Lose on seven-out
        elif roll.total() == 7:
            return BetResult(0, 0)

        # No action on other numbers
        else:
            return BetResult(0, stake)

    def _calculate_winnings(self, stake: int) -> int:
        """Calculate winnings based on true casino odds."""
        if self.number in (4, 10):
            return stake * 9 // 5  # 9:5 odds
        elif self.number in (5, 9):
            return stake * 7 // 5  # 7:5 odds
        elif self.number in (6, 8):
            return stake * 7 // 6  # 7:6 odds
        else:
            raise ValueError(f"Invalid place number: {self.number}")

    def validate(self, state: TableState, stake: int) -> None:
        """Validate place bet amount."""
        # Negative check
        if stake < 0:
            raise IllegalAction("Place bet amount cannot be negative")

        # Zero is valid (removing bet)
        if stake == 0:
            return

        # Bankroll check
        if stake > state.bankroll:
            raise IllegalAction("Place bet exceeds bankroll")

        # Table limits
        if stake < state.table_min:
            raise IllegalAction(f"Place bet below table minimum ${state.table_min}")
        if stake > state.table_max:
            raise IllegalAction(f"Place bet exceeds table maximum ${state.table_max}")

        # Increment validation
        if self.number in (6, 8):
            if stake % 6 != 0:
                raise IllegalAction(f"Place bet on {self.number} must be multiples of $6")
        else:  # 4, 5, 9, 10
            if stake % 5 != 0:
                raise IllegalAction(f"Place bet on {self.number} must be multiples of $5")
