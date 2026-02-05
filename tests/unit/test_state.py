from typing import Optional
import pytest
from craps.phase import TablePhase
from craps.state import TableConfig, TableState
from craps.dice import Roll
from craps.bets.model import Bet, requires_target
from craps.exceptions import InsufficientFunds, IllegalAction

ALL_NUMBERS = list(range(2, 13))

class DummyBets(Bet):
    """A dummy bet implementation for testing TableState."""
    def __init__(self, init_phase: TablePhase):
        super().__init__(init_phase)
        self._stake = {n: 0.0 for n in range(2, 13)}
        self._odds = {n: 0.0 for n in range(2, 13)}

    @property
    def is_prop(self) -> bool:
        return False

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

    def get_stake_targets(self):
        return tuple(ALL_NUMBERS)

    def set_stake_targets(self):
        return tuple(ALL_NUMBERS)

    def get_odds_targets(self):
        return tuple(ALL_NUMBERS)

    def set_odds_targets(self):
        return tuple(ALL_NUMBERS)

    @requires_target(ALL_NUMBERS)
    def get_stake_increment(self, target: Optional[int] = None) -> int:
        return 1

    @requires_target(ALL_NUMBERS)
    def get_odds_increment(self, target: Optional[int] = None) -> Optional[int]:
        return 1

    def can_set_stake(self, target=None) -> bool:
        return True

    def can_set_odds(self, target=None) -> bool:
        return True


class DummyPropBet(Bet):
    """A dummy prop bet implementation for testing TableState."""
    def __init__(self, init_phase: TablePhase):
        super().__init__(init_phase)
        self._stake = {n: 0.0 for n in range(2, 13)}
        self._odds = {n: 0.0 for n in range(2, 13)}

    @property
    def is_prop(self) -> bool:
        return True

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

    def get_stake_targets(self):
        return tuple(ALL_NUMBERS)

    def set_stake_targets(self):
        return tuple(ALL_NUMBERS)

    def get_odds_targets(self):
        return tuple(ALL_NUMBERS)

    def set_odds_targets(self):
        return tuple(ALL_NUMBERS)

    @requires_target(ALL_NUMBERS)
    def get_stake_increment(self, target: Optional[int] = None) -> int:
        return 1

    @requires_target(ALL_NUMBERS)
    def get_odds_increment(self, target: Optional[int] = None) -> Optional[int]:
        return 1

    def can_set_stake(self, target=None) -> bool:
        return True

    def can_set_odds(self, target=None) -> bool:
        return True


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


@pytest.fixture
def state_with_prop():
    config = TableConfig(
        table_min=25,
        table_max=10000,
        odds_max=3,
        prop_min=5
    )
    bets = {
        'dummy': DummyBets(TablePhase(point=None)),
        'prop': DummyPropBet(TablePhase(point=None))
    }
    bankroll = 50000.0
    return TableState(config, bets, bankroll)

class TestStep:
    def test_bankroll_is_paid(self, state: TableState):
        state.set_bet_stake('dummy', 30.0, target=6)
        state.step(Roll((3,3)))
        state.step(Roll((3,3)))
        assert state.get_bankroll_size() == 230.0

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
        state.set_bet_stake('dummy', 50.0, target=6)
        assert state.get_bet_stake('dummy', target=6) == 50.0
        assert state.get_bankroll_size() == 150.0
        state.set_bet_stake('dummy', 30.0, target=6)  # reduce but stay above table_min (25)
        assert state.get_bankroll_size() == 170.0

    def test_set_bet_stake_errors_if_not_enough_funds(self, state: TableState):
        with pytest.raises(InsufficientFunds):
            state.set_bet_stake('dummy', 500.0, target=6)  # within table_max but exceeds bankroll (200)

    def test_set_and_get_bet_odds_works(self, state: TableState):
        state.set_bet_stake('dummy', 100.0, target=6)  # need stake for odds_max check
        state.set_bet_odds('dummy', 30.0, target=6)
        assert state.get_bet_odds('dummy', target=6) == 30.0
        assert state.get_bankroll_size() == 70.0  # 200 - 100 - 30
        state.set_bet_odds('dummy', 25.0, target=6)  # table_min is 25
        assert state.get_bankroll_size() == 75.0  # got 5 back

    def test_set_bet_odds_errors_if_not_enough_funds(self, state: TableState):
        state.set_bet_stake('dummy', 100.0, target=6)  # bankroll now 100
        with pytest.raises(InsufficientFunds):
            state.set_bet_odds('dummy', 200.0, target=6)  # within odds_max (3*100=300), but exceeds bankroll


class TestBetLimits:
    """Tests for table_min, table_max, prop_min, and odds_max enforcement."""

    def test_set_bet_stake_rejects_below_table_min(self, state_with_prop: TableState):
        with pytest.raises(IllegalAction):
            state_with_prop.set_bet_stake('dummy', 10.0, target=6)  # table_min is 25

    def test_set_bet_stake_rejects_above_table_max(self, state_with_prop: TableState):
        with pytest.raises(IllegalAction):
            state_with_prop.set_bet_stake('dummy', 20000.0, target=6)  # table_max is 10000

    def test_set_bet_stake_accepts_at_table_min(self, state_with_prop: TableState):
        state_with_prop.set_bet_stake('dummy', 25.0, target=6)
        assert state_with_prop.get_bet_stake('dummy', target=6) == 25.0

    def test_set_bet_stake_prop_rejects_below_prop_min(self, state_with_prop: TableState):
        with pytest.raises(IllegalAction):
            state_with_prop.set_bet_stake('prop', 3.0, target=6)  # prop_min is 5

    def test_set_bet_stake_prop_accepts_at_prop_min(self, state_with_prop: TableState):
        state_with_prop.set_bet_stake('prop', 5.0, target=6)
        assert state_with_prop.get_bet_stake('prop', target=6) == 5.0

    def test_set_bet_stake_prop_accepts_between_prop_min_and_table_min(self, state_with_prop: TableState):
        state_with_prop.set_bet_stake('prop', 10.0, target=6)  # between prop_min=5 and table_min=25
        assert state_with_prop.get_bet_stake('prop', target=6) == 10.0

    def test_set_bet_stake_prop_rejects_above_table_max(self, state_with_prop: TableState):
        with pytest.raises(IllegalAction):
            state_with_prop.set_bet_stake('prop', 20000.0, target=6)  # table_max is 10000

    def test_set_bet_odds_rejects_below_table_min(self, state_with_prop: TableState):
        state_with_prop.set_bet_stake('dummy', 100.0, target=6)  # need stake for odds_max check
        with pytest.raises(IllegalAction):
            state_with_prop.set_bet_odds('dummy', 10.0, target=6)  # table_min is 25

    def test_set_bet_odds_rejects_above_table_max(self, state_with_prop: TableState):
        state_with_prop.set_bet_stake('dummy', 5000.0, target=6)  # need stake for odds_max check
        with pytest.raises(IllegalAction):
            state_with_prop.set_bet_odds('dummy', 12000.0, target=6)  # table_max is 10000

    def test_set_bet_odds_accepts_at_table_min(self, state_with_prop: TableState):
        state_with_prop.set_bet_stake('dummy', 100.0, target=6)  # need stake for odds_max check
        state_with_prop.set_bet_odds('dummy', 25.0, target=6)
        assert state_with_prop.get_bet_odds('dummy', target=6) == 25.0

    def test_set_bet_odds_prop_rejects_below_prop_min(self, state_with_prop: TableState):
        state_with_prop.set_bet_stake('prop', 100.0, target=6)  # need stake for odds_max check
        with pytest.raises(IllegalAction):
            state_with_prop.set_bet_odds('prop', 3.0, target=6)  # prop_min is 5

    def test_set_bet_odds_prop_accepts_at_prop_min(self, state_with_prop: TableState):
        state_with_prop.set_bet_stake('prop', 100.0, target=6)  # need stake for odds_max check
        state_with_prop.set_bet_odds('prop', 5.0, target=6)
        assert state_with_prop.get_bet_odds('prop', target=6) == 5.0

    def test_set_bet_odds_rejects_exceeding_odds_max(self, state_with_prop: TableState):
        state_with_prop.set_bet_stake('dummy', 30.0, target=6)
        with pytest.raises(IllegalAction):
            state_with_prop.set_bet_odds('dummy', 100.0, target=6)  # odds_max is 3x, stake is 30

    def test_set_bet_odds_accepts_at_odds_max(self, state_with_prop: TableState):
        state_with_prop.set_bet_stake('dummy', 30.0, target=6)
        state_with_prop.set_bet_odds('dummy', 90.0, target=6)  # 3x stake of 30
        assert state_with_prop.get_bet_odds('dummy', target=6) == 90.0

    def test_set_bet_stake_accepts_zero_to_take_down(self, state_with_prop: TableState):
        state_with_prop.set_bet_stake('dummy', 50.0, target=6)
        assert state_with_prop.get_bet_stake('dummy', target=6) == 50.0
        state_with_prop.set_bet_stake('dummy', 0.0, target=6)
        assert state_with_prop.get_bet_stake('dummy', target=6) == 0.0

    def test_set_bet_odds_accepts_zero_to_take_down(self, state_with_prop: TableState):
        state_with_prop.set_bet_stake('dummy', 100.0, target=6)
        state_with_prop.set_bet_odds('dummy', 50.0, target=6)
        assert state_with_prop.get_bet_odds('dummy', target=6) == 50.0
        state_with_prop.set_bet_odds('dummy', 0.0, target=6)
        assert state_with_prop.get_bet_odds('dummy', target=6) == 0.0
