from craps.bets.protocol import BetType, BetResult
from craps.state import TableState
from craps.dice import Roll
from craps.exceptions import IllegalAction


class PropBet(BetType):
    """
    Base class for one-roll proposition bets.
    Always ON (works during come-out and point phases).
    """

    def validate(self, state: TableState, stake: int) -> None:
        """Standard validation for all prop bets."""
        # Negative check
        if stake < 0:
            raise IllegalAction("Prop bet amount cannot be negative")

        # Zero is valid (removing bet)
        if stake == 0:
            return

        # Bankroll check
        if stake > state.bankroll:
            raise IllegalAction("Prop bet exceeds bankroll")

        # Prop minimum
        if stake < state.prop_min:
            raise IllegalAction(f"Prop bet below prop minimum ${state.prop_min}")

        # Table maximum
        if stake > state.table_max:
            raise IllegalAction(f"Prop bet exceeds table maximum ${state.table_max}")


class AnySeven(PropBet):
    """Any 7 - wins on any roll of 7, pays 4:1."""

    def settle(self, state: TableState, stake: int, roll: Roll) -> BetResult:
        if stake == 0:
            return BetResult(0, 0)

        if roll.total() == 7:
            return BetResult(stake + stake * 4, 0)  # Pays 4:1
        else:
            return BetResult(0, 0)


class AnyCraps(PropBet):
    """Any Craps - wins on 2, 3, or 12, pays 7:1."""

    def settle(self, state: TableState, stake: int, roll: Roll) -> BetResult:
        if stake == 0:
            return BetResult(0, 0)

        if roll.total() in (2, 3, 12):
            return BetResult(stake + stake * 7, 0)  # Pays 7:1
        else:
            return BetResult(0, 0)


class AceDeuce(PropBet):
    """Ace-Deuce (3) - wins on 3, pays 15:1."""

    def settle(self, state: TableState, stake: int, roll: Roll) -> BetResult:
        if stake == 0:
            return BetResult(0, 0)

        if roll.total() == 3:
            return BetResult(stake + stake * 15, 0)  # Pays 15:1
        else:
            return BetResult(0, 0)


class Aces(PropBet):
    """Aces (2) - wins on 2, pays 30:1."""

    def settle(self, state: TableState, stake: int, roll: Roll) -> BetResult:
        if stake == 0:
            return BetResult(0, 0)

        if roll.total() == 2:
            return BetResult(stake + stake * 30, 0)  # Pays 30:1
        else:
            return BetResult(0, 0)


class Boxcars(PropBet):
    """Boxcars (12) - wins on 12, pays 30:1."""

    def settle(self, state: TableState, stake: int, roll: Roll) -> BetResult:
        if stake == 0:
            return BetResult(0, 0)

        if roll.total() == 12:
            return BetResult(stake + stake * 30, 0)  # Pays 30:1
        else:
            return BetResult(0, 0)


class YoLeven(PropBet):
    """Yo-leven (11) - wins on 11, pays 15:1."""

    def settle(self, state: TableState, stake: int, roll: Roll) -> BetResult:
        if stake == 0:
            return BetResult(0, 0)

        if roll.total() == 11:
            return BetResult(stake + stake * 15, 0)  # Pays 15:1
        else:
            return BetResult(0, 0)


class Horn(PropBet):
    """
    Horn bet - splits equally on 2, 3, 11, 12.
    Must be divisible by 4.
    Each part pays individually:
    - 2 pays 30:1 on its portion
    - 3 pays 15:1 on its portion
    - 11 pays 15:1 on its portion
    - 12 pays 30:1 on its portion
    """

    def settle(self, state: TableState, stake: int, roll: Roll) -> BetResult:
        if stake == 0:
            return BetResult(0, 0)

        # Split into 4 equal parts
        part = stake // 4

        total = roll.total()
        if total == 2:
            # Win on 2 (pays 30:1 on that portion), lose other 3 portions
            return BetResult(part + part * 30, 0)
        elif total == 3:
            # Win on 3 (pays 15:1 on that portion), lose other 3 portions
            return BetResult(part + part * 15, 0)
        elif total == 11:
            # Win on 11 (pays 15:1 on that portion), lose other 3 portions
            return BetResult(part + part * 15, 0)
        elif total == 12:
            # Win on 12 (pays 30:1 on that portion), lose other 3 portions
            return BetResult(part + part * 30, 0)
        else:
            # Lose all 4 portions
            return BetResult(0, 0)

    def validate(self, state: TableState, stake: int) -> None:
        """Validate horn bet - must be divisible by 4."""
        # Standard validation first
        super().validate(state, stake)

        # Additional check: must be divisible by 4 (unless zero)
        if stake > 0 and stake % 4 != 0:
            raise IllegalAction("Horn bet must be divisible by 4")


class CAndE(PropBet):
    """
    C&E (Craps and Eleven) - splits equally on Any Craps and 11.
    Must be divisible by 2.
    - Any Craps portion pays 7:1
    - Eleven portion pays 15:1
    """

    def settle(self, state: TableState, stake: int, roll: Roll) -> BetResult:
        if stake == 0:
            return BetResult(0, 0)

        # Split into 2 equal parts
        part = stake // 2

        total = roll.total()
        if total in (2, 3, 12):
            # Win on Any Craps (pays 7:1 on that portion), lose Eleven portion
            return BetResult(part + part * 7, 0)
        elif total == 11:
            # Win on Eleven (pays 15:1 on that portion), lose Craps portion
            return BetResult(part + part * 15, 0)
        else:
            # Lose both portions
            return BetResult(0, 0)

    def validate(self, state: TableState, stake: int) -> None:
        """Validate C&E bet - must be divisible by 2."""
        # Standard validation first
        super().validate(state, stake)

        # Additional check: must be divisible by 2 (unless zero)
        if stake > 0 and stake % 2 != 0:
            raise IllegalAction("C&E bet must be divisible by 2")