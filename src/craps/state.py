from dataclasses import dataclass
from typing import Optional, Dict
from craps.bankroll import Bankroll
from craps.phase import TablePhase, transition_phase
from craps.dice import Roll
from craps.bets.model import Bet
from craps.exceptions import IllegalAction

@dataclass
class TableConfig:
    """
    Represents the configuration of the table such as the table min and max bets.
    """
    table_min: float
    table_max: float
    odds_max: float
    prop_min: float

class TableState:
    """
    Represents the current state of the table including bets and phase state.
    """
    def __init__(
            self,
            config: TableConfig,
            bets: Dict[str, Bet],
            init_bankroll: float
        ):
        # Config
        self.config = config

        # State
        self._phase = TablePhase()
        self._bankroll = Bankroll(init_bankroll)

        # Roll tracking
        self._roll_count = 0
        self._last_roll = None

        # Bets
        self.bets = bets

    def step(self, roll: Roll):
        """
        Progresses the simulator by one roll.
        """
        for _, bet in self.bets.items():
            winnings = bet.settle(roll)
            self._bankroll.deposit(winnings)
        
        self._phase = transition_phase(self._phase, roll)
        self._roll_count += 1
        self._last_roll = roll
    
    def set_bet_stake(self, key: str, amount: float, target: Optional[int]=None):
        if amount > self.config.table_max:
            raise IllegalAction(f"Amount {amount} is above the table max of {self.config.table_max}")
        min_bet = self.config.prop_min if self.bets[key].is_prop else self.config.table_min
        if amount != 0 and amount < min_bet:
            raise IllegalAction(f"Amount {amount} is below the minimum of {min_bet}")
        curr = self.get_bet_stake(key, target=target)
        delta = curr - amount
        self._bankroll.update(delta)
        self.bets[key].set_stake(amount, target=target)

    def get_bet_stake(self, key: str, target: Optional[int]=None) -> float:
        return self.bets[key].get_stake(target=target)

    def set_bet_odds(self, key: str, amount: float, target: Optional[int]=None):
        # Use target for stake lookup if it's in get_stake_targets, else None
        stake_targets = self.bets[key].get_stake_targets()
        stake_target = target if target in stake_targets else None
        stake = self.get_bet_stake(key, target=stake_target)
        if amount > stake * self.config.odds_max:
            raise IllegalAction(f"Amount {amount} exceeds the max odds ({self.config.odds_max}X). Current {key} stake is {stake}")
        if amount > self.config.table_max:
            raise IllegalAction(f"Amount {amount} is above the table max of {self.config.table_max}")
        min_bet = self.config.prop_min if self.bets[key].is_prop else self.config.table_min
        if amount != 0 and amount < min_bet:
            raise IllegalAction(f"Amount {amount} is below the minimum of {min_bet}")
        curr_odds = self.get_bet_odds(key, target=target)
        delta = curr_odds - amount
        self._bankroll.update(delta)
        self.bets[key].set_odds(amount, target=target)

    def get_bet_odds(self, key: str, target: Optional[int]=None) -> float:
        return self.bets[key].get_odds(target=target)

    def get_bankroll_size(self) -> float:
        return self._bankroll.get_size()
    
    def get_phase(self) -> TablePhase:
        return self._phase
    
    def get_roll_count(self) -> int:
        return self._roll_count

    def get_last_roll(self) -> Roll:
        return self._last_roll
