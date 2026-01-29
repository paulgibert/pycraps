from typing import Optional
from craps.phase import TablePhase
from craps.dice import Roll
from craps.constants import POINTS, NATURAL_WINNERS, CRAPS, SEVEN_OUT
from craps.bets.model import Bet, requires_target
from craps.bets.utils import TRUE_ODDS

class ComeBets(Bet):
    def __init__(self):
        self._pending_stake = 0
        self._stake = {n: 0.0 for n in POINTS}
        self._odds = {n: 0.0 for n in POINTS}

    def settle(self, phase: TablePhase, roll: Roll) -> float:
        """
        # TODO
        """
        total = roll.total()
        if phase.point is None:
            return 0
        
        if total in NATURAL_WINNERS:
            winnings = self._pending * 2.0
            self._clear_pending()
        elif total in CRAPS:
            winnings = 0
            self.clear_pending()
        elif total == SEVEN_OUT:
            winnings = 0
            self.clear_all()
        else:
            winnings = (self._stake[total] * 2.0) + (1.0 + TRUE_ODDS[total]) * self._odds[total]
            self.clear_target(total)
            self._move_pending(total)

        return winnings

    @requires_target(POINTS)
    def _set_stake(self, amount: float, target: Optional[None]=None):
        """
        # TODO
        """
        self._stake[target] = amount

    @requires_target(POINTS)
    def _get_stake(self, target: Optional[None]=None) -> float:
        """
        # TODO
        """
        return self._stake[target]

    @requires_target(POINTS)
    def _set_odds(self, amount: float, target: Optional[None]=None):
        """
        # TODO
        """
        self._odds[target] = amount

    @requires_target(POINTS)
    def _get_odds(self, target: Optional[None]=None) -> float:
        """
        # TODO
        """
        return self._odds[target]

    def _clear_pending(self):
        self._stake_pending = 0
    
    def _clear_target(self, target: int):
        if target not in POINTS:
            raise ValueError(f"Tried to clear come bets on invalid target: {target}")
        self._stake[target] = 0
        self._odds[target] = 0

    def _clear_all(self):
        for target in POINTS:
            self._clear_target(target)
        self._clear_pending()
    
    def _move_pending(self, target: int):
        if target not in POINTS:
            raise ValueError(f"Tried to move come pending to an invalid target: {target}")
        self._stake[target] = self._pending_stake
        self._clear_pending()
