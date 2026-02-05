import pytest
from craps.phase import TablePhase
from craps.dice import Roll
from craps.bets.pass_line import PassLine
from craps.bets.come_bets import ComeBets
from craps.bets.place_bets import PlaceBets
from craps.bets.field import Field
from craps.constants import POINTS


@pytest.fixture
def comeout():
    return TablePhase(point=None)


@pytest.fixture
def point_on_6():
    return TablePhase(point=6)


class TestPassLineCanSet:
    def test_can_set_stake_comeout(self, comeout):
        pl = PassLine(comeout)
        assert pl.can_set_stake() is True

    def test_cannot_set_stake_point_phase(self, point_on_6):
        pl = PassLine(point_on_6)
        assert pl.can_set_stake() is False

    def test_cannot_set_odds_comeout(self, comeout):
        pl = PassLine(comeout)
        pl.set_stake(30.0)
        for point in POINTS:
            assert pl.can_set_odds(target=point) is False

    def test_can_set_odds_on_matching_point_with_stake(self, comeout):
        pl = PassLine(comeout)
        pl.set_stake(30.0)
        pl.settle(Roll((3, 3)))  # establish point 6
        assert pl.can_set_odds(target=6) is True

    def test_cannot_set_odds_on_wrong_point(self, comeout):
        pl = PassLine(comeout)
        pl.set_stake(30.0)
        pl.settle(Roll((3, 3)))  # establish point 6
        assert pl.can_set_odds(target=4) is False

    def test_cannot_set_odds_without_stake(self, comeout):
        pl = PassLine(comeout)
        pl.settle(Roll((3, 3)))  # establish point 6, no stake
        assert pl.can_set_odds(target=6) is False

    def test_set_stake_zero_allowed_during_point(self, comeout):
        pl = PassLine(comeout)
        pl.set_stake(30.0)
        pl.settle(Roll((3, 3)))  # establish point 6
        pl.set_stake(0.0)  # take down — should not raise
        assert pl.get_stake() == 0.0

    def test_set_odds_zero_allowed_during_comeout(self, comeout):
        pl = PassLine(comeout)
        pl.set_odds(0.0, target=6)  # no-op take down — should not raise
        assert pl.get_odds(target=6) == 0.0

    def test_can_set_stake_forbids_target(self, comeout):
        pl = PassLine(comeout)
        with pytest.raises(ValueError):
            pl.can_set_stake(target=6)

    def test_can_set_odds_requires_target(self, comeout):
        pl = PassLine(comeout)
        with pytest.raises(ValueError):
            pl.can_set_odds()


class TestComeBetsCanSet:
    def test_cannot_set_stake_comeout(self, comeout):
        cb = ComeBets(comeout)
        assert cb.can_set_stake() is False

    def test_can_set_stake_point_phase(self, point_on_6):
        cb = ComeBets(point_on_6)
        assert cb.can_set_stake() is True

    def test_cannot_set_odds_no_established(self, point_on_6):
        cb = ComeBets(point_on_6)
        for point in POINTS:
            assert cb.can_set_odds(target=point) is False

    def test_can_set_odds_with_established_come(self, comeout):
        cb = ComeBets(comeout)
        # Establish point first, then place come bet, then settle to move it
        cb.settle(Roll((2, 2)))  # point = 4
        cb.set_stake(30.0)
        cb.settle(Roll((2, 3)))  # come moves to 5
        assert cb.can_set_odds(target=5) is True
        assert cb.can_set_odds(target=4) is False

    def test_cannot_set_odds_no_target(self, point_on_6):
        cb = ComeBets(point_on_6)
        assert cb.can_set_odds() is False

    def test_cannot_set_odds_invalid_target(self, point_on_6):
        cb = ComeBets(point_on_6)
        assert cb.can_set_odds(target=7) is False

    def test_set_stake_zero_allowed_during_comeout(self, comeout):
        cb = ComeBets(comeout)
        cb.set_stake(0.0)  # take down — should not raise
        assert cb.get_stake() == 0.0

    def test_set_odds_zero_allowed_without_established(self, point_on_6):
        cb = ComeBets(point_on_6)
        cb.set_odds(0.0, target=4)  # no-op take down — should not raise
        assert cb.get_odds(target=4) == 0.0

    def test_can_set_stake_forbids_target(self, point_on_6):
        cb = ComeBets(point_on_6)
        with pytest.raises(ValueError):
            cb.can_set_stake(target=4)


class TestPlaceBetsCanSet:
    def test_cannot_set_stake_comeout(self, comeout):
        pb = PlaceBets(comeout)
        for point in POINTS:
            assert pb.can_set_stake(target=point) is False

    def test_can_set_stake_point_phase(self, point_on_6):
        pb = PlaceBets(point_on_6)
        for point in POINTS:
            assert pb.can_set_stake(target=point) is True

    def test_cannot_set_odds(self, point_on_6):
        pb = PlaceBets(point_on_6)
        assert pb.can_set_odds() is False
        assert pb.can_set_odds(target=6) is False

    def test_set_stake_zero_allowed_during_comeout(self, comeout):
        pb = PlaceBets(comeout)
        pb.set_stake(0.0, target=6)  # take down — should not raise
        assert pb.get_stake(target=6) == 0.0

    def test_can_set_stake_requires_target(self, point_on_6):
        pb = PlaceBets(point_on_6)
        with pytest.raises(ValueError):
            pb.can_set_stake()


class TestFieldCanSet:
    def test_can_set_stake_always(self, comeout, point_on_6):
        for phase in [comeout, point_on_6]:
            f = Field(phase)
            assert f.can_set_stake() is True

    def test_cannot_set_odds(self, comeout, point_on_6):
        for phase in [comeout, point_on_6]:
            f = Field(phase)
            assert f.can_set_odds() is False

    def test_can_set_stake_forbids_target(self, comeout):
        f = Field(comeout)
        with pytest.raises(ValueError):
            f.can_set_stake(target=6)

    def test_can_set_odds_forbids_target(self, comeout):
        f = Field(comeout)
        with pytest.raises(ValueError):
            f.can_set_odds(target=6)
