from dataclasses import dataclass
from typing import Optional
from craps.bankroll import Bankroll
from craps.phase import TablePhase, transition_phase
from craps.dice import Roll
from craps.bets import (
    PassLine,
    ComeBets,
    PlaceBets,
    Field
)

@dataclass
class TableConfig:
    """
    Represents the configuration of the table such as the table min and max bets.
    """
    table_min: int
    table_max: int
    odds_max: int
    prop_min: int

class TableState:
    """
    Represents the current state of the table including bets and phase state.
    """
    def __init__(self, config: TableConfig, init_bankroll: int=1000):
        # Config
        self.config = config

        # State
        self._phase = TablePhase()
        self._bankroll = Bankroll(init_bankroll)

        # Roll tracking
        self._roll_count = 0
        self._last_roll = 0

        self._bets = {
            "pass_line'": PassLine(),
            "come_bets": ComeBets(),
            "place_bets": PlaceBets(),
            "field": Field()
        }

    def step(self, roll: Roll):
        """
        Progresses the simulator by one roll.
        """
        for _, bet in self._bets.items():
            delta, remaining = bet.settle(self._phase, roll)
            self._bankroll.deposit(delta)
            bet.set_stake(remaining)
        
        self._phase = transition_phase(self._phase, roll)
        self._roll_count += 1
        self._last_roll = roll
    
    # Check these against table config too!
    def set_bet_stake(self, key: str, amount: int, target: Optional[int]=None):
        curr = self.get_bet_stake(key, target=target)
        delta = curr - amount
        self._bankroll.update(delta)
        self.bets[key].set_stake(amount, target=target)

    def get_bet_stake(self, key: str, target: Optional[int]=None) -> int:
        return self.bets[key].get_stake(target=target)

    def set_bet_odds(self, key: str, amount: int, target: Optional[int]=None) -> int:
        curr = self.get_bet_stake(key, target=target)
        delta = curr - amount
        self._bankroll.update(delta)
        self.bets[key].set_odds(amount, target=target)

    def get_bet_odds(self, key: str, target: Optional[int]=None) -> int:
        return self.bets[key].get_odds(target=target)
