from craps.bets.protocol import BetType, BetResult
from craps.state import TableState
from craps.dice import Roll
from craps.exceptions import IllegalAction


class FieldBet(BetType):
    """
    Field bet - one-roll bet that wins on 2, 3, 4, 9, 10, 11, 12.

    Rules:
    - One-roll bet (resolves immediately, doesn't stay on table)
    - Always ON (works during come-out and point phases)
    - Wins on: 2, 3, 4, 9, 10, 11, 12
    - Loses on: 5, 6, 7, 8
    - Payouts:
      - 2: pays 2:1 (stake + 2x stake)
      - 12: pays 3:1 (stake + 3x stake)
      - 3, 4, 9, 10, 11: pays 1:1 (stake + stake)
    """

    def settle(self, state: TableState, stake: int, roll: Roll) -> BetResult:
        """Settle field bet for a given roll."""
        if stake == 0:
            return BetResult(0, 0)

        total = roll.total()

        # Win on 2 (pays 2:1)
        if total == 2:
            return BetResult(stake + stake * 2, 0)

        # Win on 12 (pays 3:1)
        elif total == 12:
            return BetResult(stake + stake * 3, 0)

        # Win on 3, 4, 9, 10, 11 (pays 1:1)
        elif total in (3, 4, 9, 10, 11):
            return BetResult(stake + stake, 0)

        # Lose on 5, 6, 7, 8
        else:
            return BetResult(0, 0)

    def validate(self, state: TableState, stake: int) -> None:
        """Validate field bet amount."""
        # Negative check
        if stake < 0:
            raise IllegalAction("Field bet amount cannot be negative")

        # Zero is valid (removing bet)
        if stake == 0:
            return

        # Bankroll check
        if stake > state.bankroll:
            raise IllegalAction("Field bet exceeds bankroll")

        # Table limits
        if stake < state.table_min:
            raise IllegalAction(f"Field bet below table minimum ${state.table_min}")
        if stake > state.table_max:
            raise IllegalAction(f"Field bet exceeds table maximum ${state.table_max}")