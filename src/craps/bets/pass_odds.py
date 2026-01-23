from craps.state import TableState
from craps.dice import Roll
from craps.bets.protocol import BetType, BetResult
from craps.exceptions import IllegalAction

class PassOdds(BetType):
    def settle(
        self,
        state: TableState,
        stake: int,
        roll: Roll
    ) -> BetResult:
        """
        Settles a pass odds bet based on the roll and current table state.

        No action on come-out roll.
        Wins when point is made (pays true odds: 2:1 for 4/10, 3:2 for 5/9, 6:5 for 6/8).
        Loses on seven-out.
        """
        # No action if no point
        if state.point is None:
            return BetResult(0, stake)

        # Point made - calculate payout based on true odds
        if roll.total() == state.point:
            if state.point in (4, 10):
                winnings = stake * 2  # 2:1
            elif state.point in (5, 9):
                winnings = stake * 3 // 2  # 3:2
            elif state.point in (6, 8):
                winnings = stake * 6 // 5  # 6:5
            else:
                raise ValueError(f"Invalid point value: {state.point}")
            return BetResult(stake + winnings, 0)

        # Seven-out - lose
        elif roll.total() == 7:
            return BetResult(0, 0)

        # Other number - no action
        else:
            return BetResult(0, stake)

    def validate(
        self,
        state: TableState,
        stake: int
    ) -> None:
        """
        Validates pass odds bet.

        Pass odds rules:
        - Cannot be negative
        - Can only be placed when point is established
        - Must have a pass line bet
        - Cannot exceed max_odds * pass_line
        - Cannot exceed bankroll
        - Must be in correct increments for clean payouts
        """
        # Check for negative bet
        if stake < 0:
            raise IllegalAction("Bet amount cannot be negative")

        # Skip other checks if stake is zero (removing odds)
        if stake == 0:
            return

        # Must have point established to place odds
        if state.point is None:
            raise IllegalAction("Cannot place odds bet without point established")

        # Must have pass line bet to place odds
        if state.bets.pass_line == 0:
            raise IllegalAction("Must have pass line bet to place odds")

        # Check max odds limit
        if stake > state.max_odds * state.bets.pass_line:
            raise IllegalAction(f"Odds bet cannot exceed {state.max_odds}x pass line bet")

        # Check bankroll
        if stake > state.bankroll:
            raise IllegalAction("Bet exceeds bankroll")

        # Check increment rules for clean payouts
        if state.point in (5, 9):
            if stake % 2 != 0:
                raise IllegalAction("Odds on point 5/9 must be even amounts")
        elif state.point in (6, 8):
            if stake % 5 != 0:
                raise IllegalAction("Odds on point 6/8 must be multiples of $5")
        # Point 4/10 can be any amount (2:1 always pays even)
