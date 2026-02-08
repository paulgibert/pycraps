import pytest
from craps.phase import TablePhase
from craps.dice import Roll
from craps.bets.pass_line import PassLine
from craps.exceptions import IllegalAction

NATURALS = [Roll((3, 4)), Roll((5, 6))]
CRAPS_ROLLS = [Roll((1, 1)), Roll((1, 2)), Roll((6, 6))]
POINT_ROLLS = [Roll((2, 2)), Roll((2, 3)), Roll((1, 5)), Roll((2, 6)), Roll((5, 4)), Roll((5, 5))]

@pytest.fixture
def comeout():
    return TablePhase(point=None)

@pytest.fixture
def pass_line_on_6(comeout):
    pl = PassLine(comeout)
    pl.set_stake(30.0)
    pl.settle(Roll((3, 3)))
    return pl


class TestSettleComeout:
    @pytest.mark.parametrize("roll", NATURALS)
    def test_natural_winner(self, roll: Roll, comeout: TablePhase):
        pl = PassLine(comeout)
        pl.set_stake(25.0)
        assert pl.settle(roll) == 50.0
        assert pl.get_stake() == 0.0

    @pytest.mark.parametrize("roll", CRAPS_ROLLS)
    def test_craps(self, roll: Roll, comeout: TablePhase):
        pl = PassLine(comeout)
        pl.set_stake(25.0)
        assert pl.settle(roll) == 0.0
        assert pl.get_stake() == 0.0

    @pytest.mark.parametrize("roll", POINT_ROLLS)
    def test_establishing_point(self, roll: Roll, comeout: TablePhase):
        pl = PassLine(comeout)
        pl.set_stake(25.0)
        assert pl.settle(roll) == 0.0
        assert pl.get_stake() == 25.0

    def test_set_odds_errors_during_comeout(self, comeout: TablePhase):
        pl = PassLine(comeout)
        pl.set_stake(30.0)
        with pytest.raises(IllegalAction):
            pl.set_odds(60.0, target=6)

    def test_initial_stake_and_odds_are_zero(self, comeout: TablePhase):
        pl = PassLine(comeout)
        assert pl.get_stake() == 0.0
        for point in [4, 5, 6, 8, 9, 10]:
            assert pl.get_odds(target=point) == 0.0

    @pytest.mark.parametrize("roll", NATURALS + CRAPS_ROLLS)
    def test_settle_with_no_stake(self, roll: Roll, comeout: TablePhase):
        pl = PassLine(comeout)
        assert pl.settle(roll) == 0.0

    def test_set_stake_with_target_errors(self, comeout: TablePhase):
        pl = PassLine(comeout)
        with pytest.raises(ValueError):
            pl.set_stake(30.0, target=6)

    def test_get_stake_with_target_errors(self, comeout: TablePhase):
        pl = PassLine(comeout)
        with pytest.raises(ValueError):
            pl.get_stake(target=6)

    def test_get_odds_without_target_errors(self, comeout: TablePhase):
        pl = PassLine(comeout)
        with pytest.raises(ValueError):
            pl.get_odds()


class TestSettlePointOn:
    @pytest.mark.parametrize(
        "point, winnings",
        [
            (Roll((2, 2)), 240.0),
            (Roll((2, 3)), 210.0),
            (Roll((1, 5)), 192.0),
            (Roll((2, 6)), 192.0),
            (Roll((5, 4)), 210.0),
            (Roll((5, 5)), 240.0),
        ],
    )
    def test_hitting_point(self, point: Roll, winnings: float, comeout: TablePhase):
        pl = PassLine(comeout)
        pl.set_stake(30.0)
        pl.settle(point)
        point_value = point.total()
        pl.set_odds(60.0, target=point_value)
        assert pl.settle(point) == winnings
        assert pl.get_stake() == 0.0
        assert pl.get_odds(target=point_value) == 0.0

    def test_seven_out(self, pass_line_on_6: PassLine):
        pass_line_on_6.set_odds(60.0, target=6)
        assert pass_line_on_6.settle(Roll((3, 4))) == 0.0
        assert pass_line_on_6.get_stake() == 0.0
        assert pass_line_on_6.get_odds(target=6) == 0.0

    def test_other_roll(self, pass_line_on_6: PassLine):
        pass_line_on_6.set_odds(60.0, target=6)
        assert pass_line_on_6.settle(Roll((2, 2))) == 0.0
        assert pass_line_on_6.get_stake() == 30.0
        assert pass_line_on_6.get_odds(target=6) == 60.0

    def test_set_stake_errors_during_point(self, pass_line_on_6: PassLine):
        with pytest.raises(IllegalAction):
            pass_line_on_6.set_stake(30.0)

    def test_set_odds_with_wrong_target_errors(self, pass_line_on_6: PassLine):
        with pytest.raises(IllegalAction):
            pass_line_on_6.set_odds(30.0, target=4)

    def test_set_odds_replaces_previous_odds(self, pass_line_on_6: PassLine):
        pass_line_on_6.set_odds(60.0, target=6)
        pass_line_on_6.set_odds(100.0, target=6)
        assert pass_line_on_6.get_odds(target=6) == 100.0

    def test_set_odds_with_zero_stake_errors(self, comeout: TablePhase):
        pl = PassLine(comeout)
        pl.settle(Roll((3, 3)))
        with pytest.raises(IllegalAction):
            pl.set_odds(30.0, target=6)

    def test_set_odds_without_target_errors(self, pass_line_on_6: PassLine):
        with pytest.raises(ValueError):
            pass_line_on_6.set_odds(30.0)

    def test_get_odds_returns_zero_for_non_point_target(self, pass_line_on_6: PassLine):
        pass_line_on_6.set_odds(60.0, target=6)
        assert pass_line_on_6.get_odds(target=4) == 0.0
        assert pass_line_on_6.get_odds(target=6) == 60.0


class TestReset:
    def test_reset_clears_stake_and_odds(self, pass_line_on_6: PassLine):
        pass_line_on_6.set_odds(60.0, target=6)
        pass_line_on_6.reset()
        assert pass_line_on_6.get_stake() == 0.0
        for point in [4, 5, 6, 8, 9, 10]:
            assert pass_line_on_6.get_odds(target=point) == 0.0

    def test_reset_restores_comeout_phase(self, pass_line_on_6: PassLine):
        pass_line_on_6.reset()
        assert pass_line_on_6._phase.point is None
        assert pass_line_on_6.can_set_stake()
