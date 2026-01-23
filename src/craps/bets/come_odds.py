from craps.bets.protocol import BetType, BetResult
from craps.state import TableState
from craps.dice import Roll
from craps.exceptions import IllegalAction

class ComeOdds(BetType):
    """
    Odds bet on an established come point.
    Pays true odds: 2:1 on 4/10, 3:2 on 5/9, 6:5 on 6/8.
    """
    def __init__(self, come_point: int):
        """
        Args:
            come_point: The point number this odds bet is for (4, 5, 6, 8, 9, or 10)
        """
        if come_point not in (4, 5, 6, 8, 9, 10):
            raise ValueError(f"Invalid come point: {come_point}")
        self.come_point = come_point

    def settle(self, state: TableState, stake: int, roll: Roll) -> BetResult:
        """
        Settle the come odds bet.
        Wins when the come point is rolled, loses on 7, stays on all other rolls.
        """
        if stake == 0:
            return BetResult(0, 0)

        if roll.total() == self.come_point:
            # Win with true odds
            if self.come_point in (4, 10):
                winnings = stake * 2
            elif self.come_point in (5, 9):
                winnings = stake * 3 // 2
            elif self.come_point in (6, 8):
                winnings = stake * 6 // 5
            else:
                raise ValueError(f"Invalid come point: {self.come_point}")
            return BetResult(stake + winnings, 0)
        elif roll.total() == 7:
            # Lose on seven-out
            return BetResult(0, 0)
        else:
            # Stays on all other rolls
            return BetResult(0, stake)

    def validate(self, state: TableState, stake: int) -> None:
        """
        Validates that the come odds bet is legal.

        Rules:
        - Cannot be negative
        - Can only place if there's a come bet on this point
        - Cannot exceed max_odds times the come bet
        - Must meet increment requirements (even for 5/9, multiples of $5 for 6/8)
        - Cannot exceed bankroll
        """
        if stake < 0:
            raise IllegalAction("Bet amount cannot be negative")

        if stake == 0:
            return

        # Get the corresponding come bet amount
        come_bet_field = f'come_{self.come_point}'
        come_bet_amount = getattr(state.bets, come_bet_field)

        if come_bet_amount == 0:
            raise IllegalAction(
                f"Cannot place odds on come point {self.come_point} without an established come bet"
            )

        # Check max odds
        if stake > state.max_odds * come_bet_amount:
            raise IllegalAction(
                f"Come odds cannot exceed {state.max_odds}x the come bet amount"
            )

        # Check bankroll
        if stake > state.bankroll:
            raise IllegalAction("Bet exceeds bankroll")

        # Increment validation
        if self.come_point in (5, 9):
            if stake % 2 != 0:
                raise IllegalAction(
                    f"Come odds on point {self.come_point} must be even amounts for proper payout"
                )
        elif self.come_point in (6, 8):
            if stake % 5 != 0:
                raise IllegalAction(
                    f"Come odds on point {self.come_point} must be multiples of $5 for proper payout"
                )