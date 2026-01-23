from craps.state import TableState
from craps.dice import Roll
from craps.bets.protocol import BetType, BetResult
from craps.exceptions import IllegalAction

class ComeBet(BetType):
    """
    Come bet has two phases:
    1. Traveling: Just placed in come area, wins on 7/11, loses on 2/3/12, establishes on 4/5/6/8/9/10
    2. Established: On a specific point, wins if that point rolls, loses on 7

    Note: This handles both phases. Use ComeTraveling for the traveling bet,
    and Come4/Come5/etc for established come bets.
    """

    def __init__(self, come_point: int | None = None):
        """
        come_point: None for traveling bet, or specific point (4,5,6,8,9,10) for established bet
        """
        self.come_point = come_point

    def settle(
        self,
        state: TableState,
        stake: int,
        roll: Roll
    ) -> BetResult:
        """
        Settles a come bet based on phase.

        Traveling phase: Wins on 7/11, loses on 2/3/12, establishes on point numbers.
        Established phase: Wins if point is rolled, loses on 7, continues otherwise.
        """
        # Traveling come bet (in come area, not on a point)
        if self.come_point is None:
            if roll.total() in (7, 11):
                return BetResult(2 * stake, 0)  # win
            elif roll.total() in (2, 3, 12):
                return BetResult(0, 0)  # lose
            elif roll.total() in (4, 5, 6, 8, 9, 10):
                # Bet travels to the point - this is handled by updating state
                # The traveling bet should be removed and a come_N bet established
                # For now, return no action (settlement doesn't move bets)
                return BetResult(0, stake)
            else:
                return BetResult(0, stake)  # shouldn't happen

        # Established come bet (on a specific point)
        else:
            if roll.total() == self.come_point:
                return BetResult(2 * stake, 0)  # win
            elif roll.total() == 7:
                return BetResult(0, 0)  # lose (seven-out)
            else:
                return BetResult(0, stake)  # no action

    def validate(
        self,
        state: TableState,
        stake: int
    ) -> None:
        """
        Validates come bet.

        Come bet rules:
        - Cannot be negative
        - Cannot exceed bankroll
        - Must be between table min and max (if non-zero)
        - Can only place when point is established (opposite of pass line)
        - Established come bets (come_4, come_5, etc.) cannot be directly placed by player
        """
        # Check for negative bet
        if stake < 0:
            raise IllegalAction("Bet amount cannot be negative")

        # For established come bets: player can never directly place or modify them
        if self.come_point is not None:
            current_stake = self._get_current_stake(state)
            if stake != current_stake:
                raise IllegalAction(
                    f"Cannot directly place or modify come bet on point {self.come_point}. "
                    "Come bets are established automatically from traveling come bets."
                )
            return  # If stake matches current, allow it (no-op)

        # Skip other checks if stake is zero
        if stake == 0:
            return

        # For traveling come bet: must have point established
        if state.point is None:
            raise IllegalAction("Cannot place come bet without point established")

        # Check bankroll
        if stake > state.bankroll:
            raise IllegalAction("Bet exceeds bankroll")

        # Check table limits
        if stake < state.table_min:
            raise IllegalAction(f"Bet below table minimum of {state.table_min}")
        if stake > state.table_max:
            raise IllegalAction(f"Bet exceeds table maximum of {state.table_max}")

    def _get_current_stake(self, state: TableState) -> int:
        """Get the current stake for this come bet from state."""
        if self.come_point == 4:
            return state.bets.come_4
        elif self.come_point == 5:
            return state.bets.come_5
        elif self.come_point == 6:
            return state.bets.come_6
        elif self.come_point == 8:
            return state.bets.come_8
        elif self.come_point == 9:
            return state.bets.come_9
        elif self.come_point == 10:
            return state.bets.come_10
        return 0


class ComeTraveling(ComeBet):
    """Traveling come bet (in come area, not yet on a point)."""
    def __init__(self):
        super().__init__(come_point=None)


class Come4(ComeBet):
    """Come bet established on point 4."""
    def __init__(self):
        super().__init__(come_point=4)


class Come5(ComeBet):
    """Come bet established on point 5."""
    def __init__(self):
        super().__init__(come_point=5)


class Come6(ComeBet):
    """Come bet established on point 6."""
    def __init__(self):
        super().__init__(come_point=6)


class Come8(ComeBet):
    """Come bet established on point 8."""
    def __init__(self):
        super().__init__(come_point=8)


class Come9(ComeBet):
    """Come bet established on point 9."""
    def __init__(self):
        super().__init__(come_point=9)


class Come10(ComeBet):
    """Come bet established on point 10."""
    def __init__(self):
        super().__init__(come_point=10)
