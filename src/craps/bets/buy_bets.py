import math
from craps.bets.protocol import BetType, BetResult
from craps.state import TableState
from craps.dice import Roll
from craps.exceptions import IllegalAction


class BuyBet(BetType):
    """
    Buy bet on a specific number (4, 5, 6, 8, 9, 10).

    Rules:
    - OFF during come-out roll (no action when state.point is None)
    - Wins when the number is rolled (stays on table after win)
    - Loses on seven-out
    - Pays true odds: 2:1 for 4/10, 3:2 for 5/9, 6:5 for 6/8
    - Charges 5% commission on win only (modern approach)
    - Commission is 5% of bet amount, rounded up to nearest dollar
    """

    def __init__(self, number: int):
        if number not in (4, 5, 6, 8, 9, 10):
            raise ValueError(f"Invalid buy number: {number}")
        self.number = number

    def settle(self, state: TableState, stake: int, roll: Roll) -> BetResult:
        """Settle buy bet for a given roll."""
        if stake == 0:
            return BetResult(0, 0)

        # OFF during come-out roll
        if state.point is None:
            return BetResult(0, stake)

        # Win if number is rolled
        if roll.total() == self.number:
            # Calculate true odds payout
            if self.number in (4, 10):
                winnings = stake * 2  # 2:1
            elif self.number in (5, 9):
                winnings = stake * 3 // 2  # 3:2
            elif self.number in (6, 8):
                winnings = stake * 6 // 5  # 6:5
            else:
                raise ValueError(f"Invalid buy number: {self.number}")

            # Calculate 5% commission on bet amount, round up to nearest dollar
            commission = math.ceil(stake * 0.05)

            # Net payout = winnings - commission (stake stays on table)
            net_payout = winnings - commission

            return BetResult(net_payout, stake)  # Stay on table

        # Lose on seven-out
        elif roll.total() == 7:
            return BetResult(0, 0)

        # No action on other numbers
        else:
            return BetResult(0, stake)

    def validate(self, state: TableState, stake: int) -> None:
        """Validate buy bet amount."""
        # Negative check
        if stake < 0:
            raise IllegalAction("Buy bet amount cannot be negative")

        # Zero is valid (removing bet)
        if stake == 0:
            return

        # Bankroll check
        if stake > state.bankroll:
            raise IllegalAction("Buy bet exceeds bankroll")

        # Table limits
        if stake < state.table_min:
            raise IllegalAction(f"Buy bet below table minimum ${state.table_min}")
        if stake > state.table_max:
            raise IllegalAction(f"Buy bet exceeds table maximum ${state.table_max}")

        # Increment validation to ensure whole dollar payouts
        if self.number in (5, 9):
            if stake % 2 != 0:
                raise IllegalAction(f"Buy bet on {self.number} must be even amounts for 3:2 payout")
        elif self.number in (6, 8):
            if stake % 5 != 0:
                raise IllegalAction(f"Buy bet on {self.number} must be multiples of $5 for 6:5 payout")
