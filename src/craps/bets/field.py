from typing import Optional
from craps.phase import TablePhase
from craps.dice import Roll
from craps.bets.model import Bet, forbids_target, forbids_odds__do_not_call

class Field(Bet):
    def __init__(self):
        self._stake = 0

    def settle(self, phase: TablePhase, roll: Roll) -> float:
        """
        # TODO
        """
        total = roll.total()
        winnings = 0
        if total in [3, 4, 9, 10, 11]:
            winnings = self._stake
        elif total == 2:
            winnings = self._stake * 2.0
        elif total == 12:
            winnings = self._stake * 3.0
        self._clear()
        return winnings
        
    @forbids_target
    def _set_stake(self, amount: float, target: Optional[None]=None):
        """
        # TODO
        """
        self._stake = amount

    @forbids_target
    def _get_stake(self, target: Optional[None]=None) -> float:
        """
        # TODO
        """
        return self._stake

    @forbids_odds__do_not_call
    def _set_odds(self, amount: float, target: Optional[None]=None):
        """
        # TODO
        """
        pass

    @forbids_odds__do_not_call
    def _get_odds(self, target: Optional[None]=None) -> float:
        """
        # TODO
        """
        pass

    def _clear(self):
        self._stake = 0
