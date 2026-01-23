import pytest
from craps.bets.come_bet import ComeTraveling, Come4, Come6
from craps.bets.protocol import BetResult
from craps.dice import Roll
from craps.exceptions import IllegalAction
from conftest import make_state


# Test ComeTraveling

traveling_bet = ComeTraveling()


@pytest.mark.parametrize("dice", [(3, 4), (5, 6)])
def test_come_traveling_natural_wins(dice):
    """Test that 7 and 11 win for traveling come bet."""
    state = make_state(point=6)  # Point must be established
    roll = Roll(dice)

    result = traveling_bet.settle(state, 10, roll)

    assert result == BetResult(bankroll_delta=20, remaining_stake=0)


@pytest.mark.parametrize("dice", [(1, 1), (1, 2), (6, 6)])
def test_come_traveling_craps_loses(dice):
    """Test that 2, 3, and 12 lose for traveling come bet."""
    state = make_state(point=6)
    roll = Roll(dice)

    result = traveling_bet.settle(state, 10, roll)

    assert result == BetResult(bankroll_delta=0, remaining_stake=0)


@pytest.mark.parametrize("dice,point_num", [
    ((2, 2), 4),
    ((2, 3), 5),
    ((3, 3), 6),
    ((4, 4), 8),
    ((4, 5), 9),
    ((5, 5), 10),
])
def test_come_traveling_establishes_point(dice, point_num):
    """Test that point numbers establish come point (bet stays)."""
    state = make_state(point=6)
    roll = Roll(dice)

    result = traveling_bet.settle(state, 10, roll)

    assert result == BetResult(bankroll_delta=0, remaining_stake=10)


def test_come_traveling_validate_no_point():
    """Test that traveling come bet requires point established."""
    state = make_state(point=None)  # No point

    with pytest.raises(IllegalAction, match="without point established"):
        traveling_bet.validate(state, 10)


def test_come_traveling_validate_legal():
    """Test that legal come bet passes validation."""
    state = make_state(point=6, bankroll=1000)

    traveling_bet.validate(state, 10)  # Should not raise


# Test Established Come Bets

come4_bet = Come4()
come6_bet = Come6()


@pytest.mark.parametrize("dice", [(1, 3), (2, 2), (3, 1)])
def test_come_4_made(dice):
    """Test that come bet on 4 wins when 4 rolls."""
    state = make_state(point=6, come_4=10)
    roll = Roll(dice)

    result = come4_bet.settle(state, 10, roll)

    assert result == BetResult(bankroll_delta=20, remaining_stake=0)


def test_come_bet_seven_out():
    """Test that come bet loses on seven-out."""
    state = make_state(point=6, come_4=10)
    roll = Roll((3, 4))  # 7

    result = come4_bet.settle(state, 10, roll)

    assert result == BetResult(bankroll_delta=0, remaining_stake=0)


def test_come_bet_other_number():
    """Test that come bet has no action on other numbers."""
    state = make_state(point=6, come_4=10)
    roll = Roll((2, 3))  # 5

    result = come4_bet.settle(state, 10, roll)

    assert result == BetResult(bankroll_delta=0, remaining_stake=10)


@pytest.mark.parametrize("dice", [(1, 5), (2, 4), (3, 3), (4, 2), (5, 1)])
def test_come_6_made(dice):
    """Test that come bet on 6 wins when 6 rolls."""
    state = make_state(point=8, come_6=10)  # Different table point
    roll = Roll(dice)

    result = come6_bet.settle(state, 10, roll)

    assert result == BetResult(bankroll_delta=20, remaining_stake=0)


def test_come_validate_exceeds_bankroll():
    """Test that come bet exceeding bankroll raises IllegalAction."""
    state = make_state(point=6, bankroll=50)

    with pytest.raises(IllegalAction, match="exceeds bankroll"):
        traveling_bet.validate(state, 100)


def test_come_validate_below_table_min():
    """Test that come bet below table min raises IllegalAction."""
    state = make_state(point=6, table_min=10)

    with pytest.raises(IllegalAction, match="table minimum"):
        traveling_bet.validate(state, 5)


def test_come_validate_negative():
    """Test that negative come bet raises IllegalAction."""
    state = make_state(point=6)

    with pytest.raises(IllegalAction, match="cannot be negative"):
        traveling_bet.validate(state, -10)


def test_come_validate_zero():
    """Test that zero come bet is valid (removing bet)."""
    state = make_state(point=6)

    traveling_bet.validate(state, 0)  # Should not raise


def test_come_cannot_directly_place_established_bet():
    """Test that player cannot directly place a come_4 bet."""
    state = make_state(point=6, come_4=0)  # No current come_4 bet

    with pytest.raises(IllegalAction, match="Cannot directly place"):
        come4_bet.validate(state, 10)


def test_come_cannot_modify_established_bet():
    """Test that player cannot modify existing come_4 bet."""
    state = make_state(point=6, come_4=10)  # Existing come_4 bet

    with pytest.raises(IllegalAction, match="Cannot directly place or modify"):
        come4_bet.validate(state, 20)  # Trying to change it


def test_come_can_keep_established_bet_same():
    """Test that keeping come_4 bet the same is allowed (no-op)."""
    state = make_state(point=6, come_4=10)

    come4_bet.validate(state, 10)  # Should not raise
