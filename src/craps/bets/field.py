from typing import Optional
from craps.phase import TablePhase
from craps.dice import Roll
from craps.bets.model import Bet, forbids_target, forbids_odds__do_not_call

class Field(Bet):
    def __init__(self, init_phase: TablePhase):
        super().__init__(init_phase)
        self._stake = 0

    def _settle(self, roll: Roll) -> float:
        """Settle the field bet based on the roll total."""
        total = roll.total()
        winnings = 0
        if total in [3, 4, 9, 10, 11]:
            winnings = self._stake * 2.0
        elif total == 2:
            winnings = self._stake * 3.0
        elif total == 12:
            winnings = self._stake * 4.0
        self._clear()
        return winnings
        
    @forbids_target
    def _set_stake(self, amount: float, target: Optional[None]=None):
        """Set the stake amount for the field bet."""
        self._stake = amount

    @forbids_target
    def _get_stake(self, target: Optional[None]=None) -> float:
        """Get the current stake amount for the field bet."""
        return self._stake

    @forbids_odds__do_not_call
    def _set_odds(self, amount: float, target: Optional[None]=None):
        """Field bets do not support odds."""
        pass

    @forbids_odds__do_not_call
    def _get_odds(self, target: Optional[None]=None) -> float:
        """Field bets do not support odds."""
        pass

    def _clear(self):
        self._stake = 0
