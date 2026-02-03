import pytest
from craps.phase import TablePhase, transition_phase
from craps.dice import Roll
from craps.constants import POINTS

NATURALS = [Roll((3, 4)), Roll((5, 6))]
CRAPS_ROLLS = [Roll((1, 1)), Roll((1, 2)), Roll((6, 6))]
POINT_ROLLS = [Roll((2, 2)), Roll((2, 3)), Roll((1, 5)), Roll((2, 6)), Roll((5, 4)), Roll((5, 5))]


class TestComeoutTransition:
    @pytest.mark.parametrize("roll", POINT_ROLLS)
    def test_point_roll_establishes_point(self, roll: Roll):
        phase = transition_phase(TablePhase(point=None), roll)
        assert phase.point == roll.total()

    @pytest.mark.parametrize("roll", NATURALS + CRAPS_ROLLS)
    def test_natural_or_craps_stays_comeout(self, roll: Roll):
        phase = transition_phase(TablePhase(point=None), roll)
        assert phase.point is None


class TestPointOnTransition:
    @pytest.mark.parametrize("point", POINTS)
    def test_hitting_point_clears(self, point: int):
        roll = Roll((point // 2, point - point // 2))
        phase = transition_phase(TablePhase(point=point), roll)
        assert phase.point is None

    def test_seven_out_clears(self):
        phase = transition_phase(TablePhase(point=6), Roll((3, 4)))
        assert phase.point is None

    @pytest.mark.parametrize("point", POINTS)
    def test_other_roll_preserves_point(self, point: int):
        # Roll a number that is neither the point nor 7
        other = 3 if point != 3 else 11
        # Build a roll that totals 'other'
        roll = Roll((1, other - 1))
        phase = transition_phase(TablePhase(point=point), roll)
        assert phase.point == point

    def test_returns_new_instance(self):
        original = TablePhase(point=6)
        result = transition_phase(original, Roll((2, 2)))
        assert result is not original
        assert result.point == 6
