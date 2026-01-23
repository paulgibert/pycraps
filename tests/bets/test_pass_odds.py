import pytest
from craps.bets.pass_odds import PassOdds
from craps.bets.protocol import BetResult
from craps.dice import Roll
from craps.exceptions import IllegalAction
from conftest import make_state


bet = PassOdds()


# Tests for settle() method

def test_settle_no_point():
    """Test that odds have no action when no point is established."""
    state = make_state(point=None)
    roll = Roll((3, 4))  # 7

    result = bet.settle(state, 30, roll)

    assert result == BetResult(bankroll_delta=0, remaining_stake=30)


@pytest.mark.parametrize("dice", [(1, 3), (2, 2), (3, 1)])
def test_settle_point_made_4(dice):
    """Test that odds on point 4 pay 2:1."""
    state = make_state(point=4, pass_line_bet=10, pass_odds_bet=30)
    roll = Roll(dice)

    result = bet.settle(state, 30, roll)

    assert result == BetResult(bankroll_delta=90, remaining_stake=0)  # $30 + $60 win


@pytest.mark.parametrize("dice", [(4, 6), (5, 5), (6, 4)])
def test_settle_point_made_10(dice):
    """Test that odds on point 10 pay 2:1."""
    state = make_state(point=10, pass_line_bet=10, pass_odds_bet=30)
    roll = Roll(dice)

    result = bet.settle(state, 30, roll)

    assert result == BetResult(bankroll_delta=90, remaining_stake=0)  # $30 + $60 win


@pytest.mark.parametrize("dice", [(1, 4), (2, 3), (3, 2), (4, 1)])
def test_settle_point_made_5(dice):
    """Test that odds on point 5 pay 3:2."""
    state = make_state(point=5, pass_line_bet=10, pass_odds_bet=30)
    roll = Roll(dice)

    result = bet.settle(state, 30, roll)

    assert result == BetResult(bankroll_delta=75, remaining_stake=0)  # $30 + $45 win


@pytest.mark.parametrize("dice", [(3, 6), (4, 5), (5, 4), (6, 3)])
def test_settle_point_made_9(dice):
    """Test that odds on point 9 pay 3:2."""
    state = make_state(point=9, pass_line_bet=10, pass_odds_bet=30)
    roll = Roll(dice)

    result = bet.settle(state, 30, roll)

    assert result == BetResult(bankroll_delta=75, remaining_stake=0)  # $30 + $45 win


@pytest.mark.parametrize("dice", [(1, 5), (2, 4), (3, 3), (4, 2), (5, 1)])
def test_settle_point_made_6(dice):
    """Test that odds on point 6 pay 6:5."""
    state = make_state(point=6, pass_line_bet=10, pass_odds_bet=30)
    roll = Roll(dice)

    result = bet.settle(state, 30, roll)

    assert result == BetResult(bankroll_delta=66, remaining_stake=0)  # $30 + $36 win


@pytest.mark.parametrize("dice", [(2, 6), (3, 5), (4, 4), (5, 3), (6, 2)])
def test_settle_point_made_8(dice):
    """Test that odds on point 8 pay 6:5."""
    state = make_state(point=8, pass_line_bet=10, pass_odds_bet=30)
    roll = Roll(dice)

    result = bet.settle(state, 30, roll)

    assert result == BetResult(bankroll_delta=66, remaining_stake=0)  # $30 + $36 win


def test_settle_seven_out():
    """Test that odds lose on seven-out."""
    state = make_state(point=6, pass_line_bet=10, pass_odds_bet=30)
    roll = Roll((3, 4))  # 7

    result = bet.settle(state, 30, roll)

    assert result == BetResult(bankroll_delta=0, remaining_stake=0)


def test_settle_other_number():
    """Test that odds have no action on other numbers."""
    state = make_state(point=6, pass_line_bet=10, pass_odds_bet=30)
    roll = Roll((2, 3))  # 5

    result = bet.settle(state, 30, roll)

    assert result == BetResult(bankroll_delta=0, remaining_stake=30)


# Tests for validate() method

def test_validate_no_point():
    """Test that odds cannot be placed without point."""
    state = make_state(point=None, pass_line_bet=10)

    with pytest.raises(IllegalAction, match="without point established"):
        bet.validate(state, 30)


def test_validate_no_pass_line():
    """Test that odds cannot be placed without pass line bet."""
    state = make_state(point=6, pass_line_bet=0)

    with pytest.raises(IllegalAction, match="Must have pass line bet"):
        bet.validate(state, 30)


def test_validate_exceeds_max_odds():
    """Test that odds cannot exceed max_odds multiplier."""
    state = make_state(point=6, pass_line_bet=10, max_odds=3)

    with pytest.raises(IllegalAction, match="cannot exceed 3x"):
        bet.validate(state, 40)


def test_validate_exceeds_bankroll():
    """Test that odds cannot exceed bankroll."""
    state = make_state(bankroll=50, point=6, pass_line_bet=10, max_odds=10)

    with pytest.raises(IllegalAction, match="exceeds bankroll"):
        bet.validate(state, 60)


def test_validate_odd_amount_on_5_9():
    """Test that odds on 5/9 must be even amounts."""
    state = make_state(point=5, pass_line_bet=10)

    with pytest.raises(IllegalAction, match="must be even amounts"):
        bet.validate(state, 31)


def test_validate_not_multiple_of_5_on_6_8():
    """Test that odds on 6/8 must be multiples of $5."""
    state = make_state(point=6, pass_line_bet=10)

    with pytest.raises(IllegalAction, match="multiples of \\$5"):
        bet.validate(state, 32)


def test_validate_legal_bet_4_10():
    """Test that legal odds on 4/10 pass validation."""
    state = make_state(point=4, pass_line_bet=10)

    bet.validate(state, 30)  # Should not raise


def test_validate_legal_bet_5_9():
    """Test that legal odds on 5/9 pass validation."""
    state = make_state(point=5, pass_line_bet=10)

    bet.validate(state, 30)  # Even amount, should not raise


def test_validate_legal_bet_6_8():
    """Test that legal odds on 6/8 pass validation."""
    state = make_state(point=6, pass_line_bet=10)

    bet.validate(state, 30)  # Multiple of 5, should not raise


def test_validate_zero_stake():
    """Test that zero stake (removing odds) is valid."""
    state = make_state(point=6, pass_line_bet=10, pass_odds_bet=30)

    bet.validate(state, 0)  # Explicitly testing zero, should not raise


def test_validate_negative_bet():
    """Test that negative odds raise IllegalAction."""
    state = make_state(point=6, pass_line_bet=10)

    with pytest.raises(IllegalAction, match="cannot be negative"):
        bet.validate(state, -10)
