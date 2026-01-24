from craps.bets.protocol import BetType, BetResult
from craps.state import TableState
from craps.dice import Roll
from craps.exceptions import IllegalAction


class HardwayBet(BetType):
    """
    Hardway bet on a specific number (4, 6, 8, 10).

    Rules:
    - Wins when the number rolls "the hard way" (as doubles)
    - Loses when the number rolls "easy" (not doubles) OR on 7
    - Multi-roll bet (stays on table until it wins or loses)
    - OFF during come-out roll
    - Payouts:
      - Hard 4 (2,2) and Hard 10 (5,5): pays 7:1
      - Hard 6 (3,3) and Hard 8 (4,4): pays 9:1
    """

    def __init__(self, number: int):
        if number not in (4, 6, 8, 10):
            raise ValueError(f"Invalid hardway number: {number}")
        self.number = number

    def settle(self, state: TableState, stake: int, roll: Roll) -> BetResult:
        """Settle hardway bet for a given roll."""
        if stake == 0:
            return BetResult(0, 0)

        # OFF during come-out roll
        if state.point is None:
            return BetResult(0, stake)

        # Win if rolled the hard way
        if roll.total() == self.number and roll[0] == roll[1]:
            # Hard 4/10 pays 7:1, Hard 6/8 pays 9:1
            if self.number in (4, 10):
                return BetResult(stake + stake * 7, 0)
            else:  # 6, 8
                return BetResult(stake + stake * 9, 0)

        # Lose if rolled easy way or 7
        elif roll.total() == self.number or roll.total() == 7:
            return BetResult(0, 0)

        # No action on other numbers
        else:
            return BetResult(0, stake)

    def validate(self, state: TableState, stake: int) -> None:
        """Validate hardway bet amount."""
        # Negative check
        if stake < 0:
            raise IllegalAction("Hardway bet amount cannot be negative")

        # Zero is valid (removing bet)
        if stake == 0:
            return

        # Bankroll check
        if stake > state.bankroll:
            raise IllegalAction("Hardway bet exceeds bankroll")

        # Prop minimum
        if stake < state.prop_min:
            raise IllegalAction(f"Hardway bet below prop minimum ${state.prop_min}")

        # Table maximum
        if stake > state.table_max:
            raise IllegalAction(f"Hardway bet exceeds table maximum ${state.table_max}")