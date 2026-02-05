import pytest
from craps.exceptions import IllegalAction
from craps.phase import TablePhase, transition_phase
from craps.bets.come_bets import ComeBets
from craps.dice import Roll
from craps.constants import POINTS

NATURAL_ROLLS = [Roll((3, 4)), Roll((5, 6))]
CRAPS_ROLLS = [Roll((1, 1)), Roll((1, 2)), Roll((6, 6))]
POINT_ROLLS = [Roll((2, 2)), Roll((2, 3)), Roll((1, 5)), Roll((2, 6)), Roll((5, 4)), Roll((5, 5))]

@pytest.fixture
def comeout():
    return TablePhase(point=None)

@pytest.fixture
def point_on_6(comeout):
    return transition_phase(comeout, Roll((3, 3)))


class TestComeout:
    @pytest.mark.parametrize("roll", NATURAL_ROLLS + CRAPS_ROLLS + POINT_ROLLS)
    def test_settle_zero_winnings_on_comeout(self, roll: Roll, comeout: TablePhase):
        come = ComeBets(comeout)
        assert come.settle(roll) == 0.0

    def test_set_stake_errors(self, comeout: TablePhase):
        come = ComeBets(comeout)
        with pytest.raises(IllegalAction):
            come.set_stake(30.0)

    def test_set_odds_errors(self, comeout: TablePhase):
        come = ComeBets(comeout)
        with pytest.raises(IllegalAction):
            come.set_odds(0.0)

    def test_initial_state_is_zero(self, comeout: TablePhase):
        come = ComeBets(comeout)
        assert come.get_stake(target=None) == 0.0
        for tgt in POINTS:
            assert come.get_stake(target=tgt) == 0.0
            assert come.get_odds(target=tgt) == 0.0


class TestPointOn:
    @pytest.mark.parametrize("roll", NATURAL_ROLLS)
    def test_settle_natural_winner(self, roll: Roll, point_on_6: TablePhase):
        come = ComeBets(point_on_6)
        come.set_stake(30.0)
        assert come.settle(roll) == 60.0
        assert come.get_stake(target=None) == 0.0
        for tgt in POINTS:
            assert come.get_stake(target=tgt) == 0.0

    @pytest.mark.parametrize("roll", CRAPS_ROLLS)
    def test_settle_craps(self, roll: Roll, point_on_6: TablePhase):
        come = ComeBets(point_on_6)
        come.set_stake(30.0)
        assert come.settle(roll) == 0.0
        assert come.get_stake(target=None) == 0.0
        for tgt in POINTS:
            assert come.get_stake(target=tgt) == 0.0

    def test_settle_seven_out(self, point_on_6: TablePhase):
        come = ComeBets(point_on_6)

        come_rolls = [Roll((2, 2)), Roll((2, 3)), Roll((2, 6)), Roll((5, 4)), Roll((5, 5))]
        come_targets = [4, 5, 8, 9, 10]
        for roll in come_rolls:
            come.set_stake(30.0, target=None)
            assert come.settle(roll) == 0.0
            assert come.get_stake(target=roll.total()) == 30.0

        for tgt in come_targets:
            come.set_odds(60.0, target=tgt)
            assert come.get_odds(target=tgt) == 60.0

        assert come.settle(Roll((3, 4))) == 0.0
        assert come.get_stake(target=None) == 0.0
        for tgt in come_targets:
            assert come.get_stake(target=tgt) == 0.0
            assert come.get_odds(target=tgt) == 0.0

    @pytest.mark.parametrize("roll", POINT_ROLLS)
    def test_settle_come_point_set(self, roll: Roll, point_on_6: TablePhase):
        come = ComeBets(point_on_6)
        come.set_stake(30.0, target=None)
        assert come.settle(roll) == 0.0
        assert come.get_stake(target=roll.total()) == 30.0

    def test_set_stake_works(self, point_on_6: TablePhase):
        come = ComeBets(point_on_6)
        come.set_stake(30.0, target=None)
        assert come.get_stake(target=None) == 30.0

    def test_set_stake_with_target_errors(self, point_on_6: TablePhase):
        come = ComeBets(point_on_6)
        with pytest.raises(ValueError):
            come.set_stake(30.0, target=6)

    @pytest.mark.parametrize("roll", POINT_ROLLS)
    def test_set_odds_on_come_point_works(self, roll: Roll, point_on_6: TablePhase):
        come = ComeBets(point_on_6)
        come.set_stake(30.0, target=None)
        come.settle(roll)
        come.set_odds(60.0, target=roll.total())
        assert come.get_odds(target=roll.total()) == 60.0
        come.set_odds(0.0, target=roll.total())
        assert come.get_odds(target=roll.total()) == 0.0

    def test_set_odds_with_no_target_fails(self, point_on_6: TablePhase):
        come = ComeBets(point_on_6)
        come.set_stake(30.0, target=None)
        come.settle(Roll((4, 4)))
        with pytest.raises(IllegalAction):
            come.set_odds(60.0, target=None)

    def test_set_odds_on_wrong_come_point_errors(self, point_on_6: TablePhase):
        come = ComeBets(point_on_6)
        come.set_stake(30.0, target=None)
        come.settle(Roll((4, 4)))
        with pytest.raises(IllegalAction):
            come.set_odds(60.0, target=6)

    @pytest.mark.parametrize(
        "roll, winnings",
        [
            (Roll((2, 2)), 240.0),
            (Roll((2, 3)), 210.0),
            (Roll((2, 6)), 192.0),
            (Roll((5, 4)), 210.0),
            (Roll((5, 5)), 240.0),
        ],
    )
    def test_hitting_come_point(self, roll: Roll, winnings: float, point_on_6: TablePhase):
        come = ComeBets(point_on_6)
        come.set_stake(30.0, target=None)
        come.settle(roll)
        come.set_odds(60.0, target=roll.total())
        assert come.settle(roll) == winnings
        assert come.get_stake(target=roll.total()) == 0.0
        assert come.get_odds(target=roll.total()) == 0.0

    def test_hitting_come_point_on_6(self, comeout: TablePhase):
        point_on_4 = transition_phase(comeout, Roll((2, 2)))
        come = ComeBets(point_on_4)
        come.set_stake(30.0, target=None)
        come.settle(Roll((1, 5)))
        come.set_odds(60.0, target=6)
        assert come.settle(Roll((1, 5))) == 192.0
        assert come.get_stake(target=6) == 0.0
        assert come.get_odds(target=6) == 0.0

    def test_seven_out_with_pending_pays_pending(self, point_on_6: TablePhase):
        come = ComeBets(point_on_6)
        come.set_stake(30.0, target=None)
        come.settle(Roll((2, 2)))
        come.set_stake(25.0, target=None)
        assert come.settle(Roll((3, 4))) == 50.0
        assert come.get_stake(target=None) == 0.0
        assert come.get_stake(target=4) == 0.0

    def test_other_roll_preserves_come_bets(self, point_on_6: TablePhase):
        come = ComeBets(point_on_6)
        come.set_stake(30.0, target=None)
        come.settle(Roll((2, 2)))
        come.set_odds(60.0, target=4)
        assert come.settle(Roll((2, 3))) == 0.0
        assert come.get_stake(target=4) == 30.0
        assert come.get_odds(target=4) == 60.0

    def test_get_stake_invalid_target_errors(self, point_on_6: TablePhase):
        come = ComeBets(point_on_6)
        with pytest.raises(ValueError):
            come.get_stake(target=3)

    def test_get_odds_no_target_errors(self, point_on_6: TablePhase):
        come = ComeBets(point_on_6)
        with pytest.raises(IllegalAction):
            come.get_odds(target=None)

    def test_get_odds_invalid_target_errors(self, point_on_6: TablePhase):
        come = ComeBets(point_on_6)
        with pytest.raises(ValueError):
            come.get_odds(target=3)
