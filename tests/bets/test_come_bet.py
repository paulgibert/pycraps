import pytest
from craps.bets.come_bets import ComeTraveling, Come4, Come6
from craps.bets.model import BetResult
from craps.dice import Roll
from craps.exceptions import InsufficientFunds
from conftest import make_state


# Test ComeTraveling

@pytest.mark.parametrize("dice", [(3, 4), (5, 6)])
def test_come_traveling_natural_wins(dice):
    """Test that 7 and 11 win for traveling come bet."""
    state = make_state(point=6)  # Point must be established
    bet = ComeTraveling(stake=10)
    roll = Roll(dice)

    result = bet.settle(state, roll)

    assert result == BetResult(bankroll_delta=20, remaining_stake=0)


@pytest.mark.parametrize("dice", [(1, 1), (1, 2), (6, 6)])
def test_come_traveling_craps_loses(dice):
    """Test that 2, 3, and 12 lose for traveling come bet."""
    state = make_state(point=6)
    bet = ComeTraveling(stake=10)
    roll = Roll(dice)

    result = bet.settle(state, roll)

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
    bet = ComeTraveling(stake=10)
    roll = Roll(dice)

    result = bet.settle(state, roll)

    assert result == BetResult(bankroll_delta=0, remaining_stake=10)


def test_come_traveling_validate_no_point():
    """Test that traveling come bet requires point established."""
    state = make_state(point=None)  # No point
    bet = ComeTraveling(stake=10)

    with pytest.raises(InsufficientFunds, match="without point established"):
        bet.validate(state)


def test_come_traveling_validate_legal():
    """Test that legal come bet passes validation."""
    state = make_state(point=6, bankroll=1000)
    bet = ComeTraveling(stake=10)

    bet.validate(state)  # Should not raise


# Test Established Come Bets

@pytest.mark.parametrize("dice", [(1, 3), (2, 2), (3, 1)])
def test_come_4_made(dice):
    """Test that come bet on 4 wins when 4 rolls."""
    state = make_state(point=6, come_4=10)
    bet = Come4(stake=10)
    roll = Roll(dice)

    result = bet.settle(state, roll)

    assert result == BetResult(bankroll_delta=20, remaining_stake=0)


def test_come_bet_seven_out():
    """Test that come bet loses on seven-out."""
    state = make_state(point=6, come_4=10)
    bet = Come4(stake=10)
    roll = Roll((3, 4))  # 7

    result = bet.settle(state, roll)

    assert result == BetResult(bankroll_delta=0, remaining_stake=0)


def test_come_bet_other_number():
    """Test that come bet has no action on other numbers."""
    state = make_state(point=6, come_4=10)
    bet = Come4(stake=10)
    roll = Roll((2, 3))  # 5

    result = bet.settle(state, roll)

    assert result == BetResult(bankroll_delta=0, remaining_stake=10)


@pytest.mark.parametrize("dice", [(1, 5), (2, 4), (3, 3), (4, 2), (5, 1)])
def test_come_6_made(dice):
    """Test that come bet on 6 wins when 6 rolls."""
    state = make_state(point=8, come_6=10)  # Different table point
    bet = Come6(stake=10)
    roll = Roll(dice)

    result = bet.settle(state, roll)

    assert result == BetResult(bankroll_delta=20, remaining_stake=0)


def test_come_validate_exceeds_bankroll():
    """Test that come bet exceeding bankroll raises IllegalAction."""
    state = make_state(point=6, bankroll=50)
    bet = ComeTraveling(stake=100)

    with pytest.raises(InsufficientFunds, match="exceeds bankroll"):
        bet.validate(state)


def test_come_validate_below_table_min():
    """Test that come bet below table min raises IllegalAction."""
    state = make_state(point=6, table_min=10)
    bet = ComeTraveling(stake=5)

    with pytest.raises(InsufficientFunds, match="table minimum"):
        bet.validate(state)


def test_come_validate_negative():
    """Test that negative come bet raises IllegalAction."""
    state = make_state(point=6)
    bet = ComeTraveling(stake=-10)

    with pytest.raises(InsufficientFunds, match="cannot be negative"):
        bet.validate(state)


def test_come_validate_zero():
    """Test that zero come bet is valid (removing bet)."""
    state = make_state(point=6)
    bet = ComeTraveling(stake=0)

    bet.validate(state)  # Should not raise


def test_come_cannot_directly_place_established_bet():
    """Test that player cannot directly place a come_4 bet."""
    state = make_state(point=6, come_4=0)  # No current come_4 bet
    bet = Come4(stake=10)

    with pytest.raises(InsufficientFunds, match="Cannot directly place"):
        bet.validate(state)


def test_come_cannot_modify_established_bet():
    """Test that player cannot modify existing come_4 bet."""
    state = make_state(point=6, come_4=10)  # Existing come_4 bet
    bet = Come4(stake=20)

    with pytest.raises(InsufficientFunds, match="Cannot directly place or modify"):
        bet.validate(state)


def test_come_can_keep_established_bet_same():
    """Test that keeping come_4 bet the same is allowed (no-op)."""
    state = make_state(point=6, come_4=10)
    bet = Come4(stake=10)

    bet.validate(state)  # Should not raise
