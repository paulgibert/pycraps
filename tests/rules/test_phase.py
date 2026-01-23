from craps.rules.phase import update_phase
from craps.dice import Roll
from conftest import make_state


def test_point_established():
    """Test that rolling a point number establishes the point."""
    state = make_state(point=None)
    roll = Roll((3, 3))  # 6

    next_state = update_phase(state, roll)

    assert next_state.point == 6


def test_no_point_on_natural():
    """Test that rolling 7 on come-out does not establish point."""
    state = make_state(point=None)
    roll = Roll((3, 4))  # 7

    next_state = update_phase(state, roll)

    assert next_state.point is None


def test_no_point_on_craps():
    """Test that rolling craps on come-out does not establish point."""
    state = make_state(point=None)
    roll = Roll((1, 1))  # 2

    next_state = update_phase(state, roll)

    assert next_state.point is None


def test_point_made():
    """Test that rolling the point clears it."""
    state = make_state(point=6)
    roll = Roll((2, 4))  # 6

    next_state = update_phase(state, roll)

    assert next_state.point is None


def test_seven_out():
    """Test that rolling 7 when point is established clears the point."""
    state = make_state(point=6)
    roll = Roll((3, 4))  # 7

    next_state = update_phase(state, roll)

    assert next_state.point is None


def test_other_number_during_point():
    """Test that rolling other numbers during point does not change point."""
    state = make_state(point=6)
    roll = Roll((2, 3))  # 5

    next_state = update_phase(state, roll)

    assert next_state.point == 6
