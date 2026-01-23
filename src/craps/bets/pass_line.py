from craps.state import TableState
from craps.dice import Roll
from craps.bets.protocol import BetType, BetResult
from craps.exceptions import IllegalAction

class PassLine(BetType):
    def settle(
        self,
        state: TableState,
        stake: int,
        roll: Roll
    ) -> BetResult:
        """
        Settles a pass line bet based on the roll and current table state.

        Come-out roll (no point): Wins on 7/11, loses on 2/3/12, establishes point otherwise.
        Point established: Wins if point is rolled, loses on 7, continues otherwise.
        """
        if state.point is None:
            # 7/11 win, 2/3/12 lose, otherwise establish point
            if roll.total() in (7, 11):
                return BetResult(2 * stake, 0)  # win
            elif roll.total() in (2, 3, 12):
                return BetResult(0, 0)  # lose
            else:
                return BetResult(0, stake)  # point established

        elif roll.total() == state.point:
            return BetResult(2 * stake, 0) # win

        elif roll.total() == 7:
            return BetResult(0, 0) # lose

        else:
            return BetResult(0, stake) # do nothing

    def validate(
        self,
        state: TableState,
        stake: int
    ) -> None:
        """
        Validates pass line bet.

        Pass line rules:
        - Cannot be negative
        - Cannot exceed bankroll
        - Must be between table min and max (if non-zero)
        - Cannot be changed once point is established
        """
        # Check for negative bet
        if stake < 0:
            raise IllegalAction("Bet amount cannot be negative")

        # Check if bet exceeds bankroll
        if stake > state.bankroll:
            raise IllegalAction("Bet exceeds bankroll")

        # Check table limits (only if bet is non-zero)
        if stake > 0:
            if stake < state.table_min:
                raise IllegalAction(f"Bet below table minimum of {state.table_min}")
            if stake > state.table_max:
                raise IllegalAction(f"Bet exceeds table maximum of {state.table_max}")

        # Check phase rules: cannot change pass line bet when point is established
        if state.point is not None:
            if stake != state.bets.pass_line:
                raise IllegalAction("Cannot change pass line bet when point is established")