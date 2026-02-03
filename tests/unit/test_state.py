from typing import Optional
import pytest
from craps.phase import TablePhase
from craps.state import TableConfig, TableState
from craps.dice import Roll
from craps.bets.model import Bet, requires_target
from craps.exceptions import InsufficientFunds

ALL_NUMBERS = list(range(2, 13))

class DummyBets(Bet):
    """A dummy bet implementation for testing TableState."""
    def __init__(self, init_phase: TablePhase):
        super().__init__(init_phase)
        self._stake = {n: 0.0 for n in range(2, 13)}
        self._odds = {n: 0.0 for n in range(2, 13)}
    
    def _settle(self, roll: Roll):
        total = roll.total()
        return self._stake[total] + self._odds[total]
    
    @requires_target(ALL_NUMBERS)
    def _set_stake(self, amount: float, target: Optional[int] = None):
        self._stake[target] = amount

    @requires_target(ALL_NUMBERS)
    def _get_stake(self, target: Optional[int] = None) -> float:
        return self._stake[target]

    @requires_target(ALL_NUMBERS)
    def _set_odds(self, amount: float, target: Optional[int] = None):
        self._odds[target] = amount

    @requires_target(ALL_NUMBERS)
    def _get_odds(self, target: Optional[int] = None) -> float:
        return self._odds[target]

@pytest.fixture
def state():
    config = TableConfig(
        table_min=25,
        table_max=10000,
        odds_max=3,
        prop_min=5
    )
    bets = {'dummy': DummyBets(TablePhase(point=None))}
    bankroll = 200.0
    return TableState(config, bets, bankroll)

class TestStep:
    def test_bankroll_is_paid(self, state: TableState):
        state.set_bet_stake('dummy', 30.0, target=6)
        state.step(Roll((3,3)))
        state.step(Roll((3,3)))
        assert state.get_bankroll().get_size() == 230.0

    def test_phase_is_transitioned(self, state: TableState):
        state.step(Roll((4,2)))
        assert state.get_phase().point == 6

    def test_last_roll_is_set(self, state: TableState):
        state.step(Roll((4,2)))
        assert state.get_last_roll() == Roll((4,2))

    def test_roll_count_is_incremented(self, state: TableState):
        assert state.get_roll_count() == 0
        state.step(Roll((4,2)))
        state.step(Roll((3,3)))
        state.step(Roll((4,3)))
        state.step(Roll((6,6)))
        state.step(Roll((1,1)))
        state.step(Roll((3,1)))
        assert state.get_roll_count() == 6

class TestGettersAndSetters:
    def test_set_and_get_bet_stake_works(self, state: TableState):
        state.set_bet_stake('dummy', 30.0, target=6)
        assert state.get_bet_stake('dummy', target=6) == 30.0
        assert state.get_bankroll().get_size() == 170.0
        state.set_bet_stake('dummy', 15.0, target=6)
        assert state.get_bankroll().get_size() == 185.0

    def test_set_bet_stake_errors_if_not_enough_funds(self, state: TableState):
        with pytest.raises(InsufficientFunds):
            state.set_bet_stake('dummy', 999999.0, target=6)

    def test_set_and_get_bet_odds_works(self, state: TableState):
        state.set_bet_odds('dummy', 30.0, target=6)
        assert state.get_bet_odds('dummy', target=6) == 30.0
        assert state.get_bankroll().get_size() == 170.0
        state.set_bet_odds('dummy', 15.0, target=6)
        assert state.get_bankroll().get_size() == 185.0

    def test_set_bet_odds_errors_if_not_enough_funds(self, state: TableState):
        with pytest.raises(InsufficientFunds):
            state.set_bet_odds('dummy', 999999.0, target=6)
