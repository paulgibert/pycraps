import pytest
from craps.env import step
from craps.action import Action
from craps.bets.model import Bets
from craps.dice import Roll
from craps.exceptions import IllegalAction
from conftest import make_state


def test_natural_winner():
    """Test that rolling 7 on come-out wins."""
    state = make_state(bankroll=1000)
    action = Action(bets=Bets(pass_line=10))
    roll = Roll((3, 4))  # 7

    next_state = step(state, action, roll)

    assert next_state.bankroll == 1010  # Won 10
    assert next_state.bets.pass_line == 0  # Bet resolved
    assert next_state.point is None  # No point established
    assert next_state.last_roll == roll
    assert next_state.roll_count == 1


def test_craps_loses():
    """Test that rolling 2 on come-out loses."""
    state = make_state(bankroll=1000)
    action = Action(bets=Bets(pass_line=10))
    roll = Roll((1, 1))  # 2

    next_state = step(state, action, roll)

    assert next_state.bankroll == 990  # Lost 10
    assert next_state.bets.pass_line == 0
    assert next_state.point is None


def test_point_established():
    """Test that rolling a point number establishes the point."""
    state = make_state(bankroll=1000)
    action = Action(bets=Bets(pass_line=10))
    roll = Roll((3, 3))  # 6

    next_state = step(state, action, roll)

    assert next_state.bankroll == 990  # Bet taken from bankroll
    assert next_state.bets.pass_line == 10  # Bet remains
    assert next_state.point == 6  # Point established
    assert next_state.last_roll == roll
    assert next_state.roll_count == 1


def test_point_made():
    """Test that hitting the point wins."""
    state = make_state(bankroll=990, point=6, pass_line_bet=10)
    action = Action(bets=Bets(pass_line=10))  # Keep same bet
    roll = Roll((2, 4))  # 6 (the point)

    next_state = step(state, action, roll)

    assert next_state.bankroll == 1010  # Won 20 (stake + winnings)
    assert next_state.bets.pass_line == 0  # Bet resolved
    assert next_state.point is None  # Point cleared


def test_seven_out():
    """Test that rolling 7 when point is established loses."""
    state = make_state(bankroll=990, point=6, pass_line_bet=10)
    action = Action(bets=Bets(pass_line=10))
    roll = Roll((3, 4))  # 7

    next_state = step(state, action, roll)

    assert next_state.bankroll == 990  # Lost stake
    assert next_state.bets.pass_line == 0  # Bet resolved
    assert next_state.point is None  # Point cleared


def test_illegal_negative_bet():
    """Test that negative bet amounts raise IllegalAction."""
    state = make_state(bankroll=1000)
    action = Action(bets=Bets(pass_line=-10))
    roll = Roll((3, 4))

    with pytest.raises(IllegalAction):
        step(state, action, roll)


def test_illegal_exceeds_bankroll():
    """Test that bets exceeding bankroll raise IllegalAction."""
    state = make_state(bankroll=100)
    action = Action(bets=Bets(pass_line=200))
    roll = Roll((3, 4))

    with pytest.raises(IllegalAction):
        step(state, action, roll)


def test_illegal_below_table_min():
    """Test that bets below table minimum raise IllegalAction."""
    state = make_state(bankroll=1000, table_min=10)
    action = Action(bets=Bets(pass_line=5))
    roll = Roll((3, 4))

    with pytest.raises(IllegalAction):
        step(state, action, roll)


def test_illegal_above_table_max():
    """Test that bets above table maximum raise IllegalAction."""
    state = make_state(bankroll=10000, table_max=500)
    action = Action(bets=Bets(pass_line=1000))
    roll = Roll((3, 4))

    with pytest.raises(IllegalAction):
        step(state, action, roll)


def test_illegal_change_bet_during_point():
    """Test that changing pass line bet when point is established raises IllegalAction."""
    state = make_state(bankroll=990, point=6, pass_line_bet=10)
    action = Action(bets=Bets(pass_line=20))  # Trying to change bet
    roll = Roll((2, 3))

    with pytest.raises(IllegalAction):
        step(state, action, roll)
