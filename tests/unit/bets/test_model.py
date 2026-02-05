import pytest
from typing import Optional
from craps.phase import TablePhase
from craps.dice import Roll
from craps.bets.model import Bet, requires_target, forbids_target, forbids_odds__do_not_call


# Concrete subclass for testing the abstract Bet base class
class DummyBet(Bet):
    def __init__(self, init_phase: TablePhase):
        super().__init__(init_phase)
        self.stake = 0.0
        self.odds = 0.0

    @property
    def is_prop(self) -> bool:
        return False

    def _settle(self, roll: Roll) -> float:
        return 0.0

    def _set_stake(self, amount: float, target: Optional[None] = None):
        self.stake = amount

    def _get_stake(self, target: Optional[None] = None) -> float:
        return self.stake

    def _set_odds(self, amount: float, target: Optional[None] = None):
        self.odds = amount

    def _get_odds(self, target: Optional[None] = None) -> float:
        return self.odds

    def get_stake_targets(self):
        return (None,)

    def set_stake_targets(self):
        return (None,)

    def get_odds_targets(self):
        return (None,)

    def set_odds_targets(self):
        return (None,)

    @forbids_target
    def get_stake_increment(self, target: Optional[int] = None) -> int:
        return 1

    @forbids_target
    def get_odds_increment(self, target: Optional[int] = None) -> Optional[int]:
        return 1

    def can_set_stake(self, target=None) -> bool:
        return True

    def can_set_odds(self, target=None) -> bool:
        return True


@pytest.fixture
def comeout():
    return TablePhase(point=None)


class TestBetBase:
    def test_set_stake_delegates(self, comeout: TablePhase):
        bet = DummyBet(comeout)
        bet.set_stake(50.0)
        assert bet.stake == 50.0

    def test_get_stake_delegates(self, comeout: TablePhase):
        bet = DummyBet(comeout)
        bet.stake = 75.0
        assert bet.get_stake() == 75.0

    def test_set_stake_negative_errors(self, comeout: TablePhase):
        bet = DummyBet(comeout)
        with pytest.raises(ValueError):
            bet.set_stake(-1.0)

    def test_set_odds_delegates(self, comeout: TablePhase):
        bet = DummyBet(comeout)
        bet.set_odds(100.0)
        assert bet.odds == 100.0

    def test_get_odds_delegates(self, comeout: TablePhase):
        bet = DummyBet(comeout)
        bet.odds = 200.0
        assert bet.get_odds() == 200.0

    def test_set_odds_negative_errors(self, comeout: TablePhase):
        bet = DummyBet(comeout)
        with pytest.raises(ValueError):
            bet.set_odds(-1.0)

    def test_settle_returns_result_and_advances_phase(self, comeout: TablePhase):
        bet = DummyBet(comeout)
        result = bet.settle(Roll((2, 2)))
        assert result == 0.0
        assert bet._phase.point == 4

    def test_settle_advances_phase_on_seven_out(self):
        bet = DummyBet(TablePhase(point=6))
        bet.settle(Roll((3, 4)))
        assert bet._phase.point is None

    def test_settle_no_phase_change_on_neutral_roll(self):
        bet = DummyBet(TablePhase(point=6))
        bet.settle(Roll((2, 2)))
        assert bet._phase.point == 6


class TestRequiresTarget:
    def test_passes_with_valid_target(self):
        class Stub:
            @requires_target((4, 5, 6))
            def method(self, target=None):
                return target
        assert Stub().method(target=4) == 4

    def test_errors_with_no_target(self):
        class Stub:
            @requires_target((4, 5, 6))
            def method(self, target=None):
                return target
        with pytest.raises(ValueError, match="target"):
            Stub().method(target=None)

    def test_errors_with_invalid_target(self):
        class Stub:
            @requires_target((4, 5, 6))
            def method(self, target=None):
                return target
        with pytest.raises(ValueError):
            Stub().method(target=99)


class TestForbidsTarget:
    def test_passes_with_no_target(self):
        class Stub:
            @forbids_target
            def method(self, target=None):
                return 42
        assert Stub().method(target=None) == 42

    def test_errors_with_target(self):
        class Stub:
            @forbids_target
            def method(self, target=None):
                return 42
        with pytest.raises(ValueError):
            Stub().method(target=6)


class TestForbidsOdds:
    def test_always_errors(self):
        class Stub:
            @forbids_odds__do_not_call
            def method(self):
                pass
        with pytest.raises(RuntimeError):
            Stub().method()
