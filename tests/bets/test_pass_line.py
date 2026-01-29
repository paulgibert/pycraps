import pytest
from craps.bets.pass_line import PassLine
from craps.bets.model import BetResult
from craps.dice import Roll
from craps.exceptions import InsufficientFunds
from conftest import make_state


# Tests for settle() method

@pytest.mark.parametrize("dice", [(3, 4), (5, 6)])
def test_settle_come_out_natural_wins(dice):
    """Test that 7 and 11 on come-out win."""
    state = make_state(point=None)
    bet = PassLine(stake=10)
    roll = Roll(dice)

    result = bet.settle(state, roll)

    assert result == BetResult(bankroll_delta=20, remaining_stake=0)


@pytest.mark.parametrize("dice", [(1, 1), (1, 2), (6, 6)])
def test_settle_come_out_craps_loses(dice):
    """Test that 2, 3, and 12 on come-out lose."""
    state = make_state(point=None)
    bet = PassLine(stake=10)
    roll = Roll(dice)

    result = bet.settle(state, roll)

    assert result == BetResult(bankroll_delta=0, remaining_stake=0)


@pytest.mark.parametrize("dice,point", [
    ((2, 2), 4),
    ((2, 3), 5),
    ((3, 3), 6),
    ((4, 4), 8),
    ((4, 5), 9),
    ((5, 5), 10),
])
def test_settle_come_out_point_established(dice, point):
    """Test that point numbers establish the point without changing the bet."""
    state = make_state(point=None)
    bet = PassLine(stake=10)
    roll = Roll(dice)

    result = bet.settle(state, roll)

    assert result == BetResult(bankroll_delta=0, remaining_stake=10)


def test_settle_point_made():
    """Test that hitting the point wins."""
    state = make_state(point=6)
    bet = PassLine(stake=10)
    roll = Roll((3, 3))  # 6

    result = bet.settle(state, roll)

    assert result == BetResult(bankroll_delta=20, remaining_stake=0)


def test_settle_seven_out():
    """Test that rolling 7 during point loses."""
    state = make_state(point=6)
    bet = PassLine(stake=10)
    roll = Roll((3, 4))  # 7

    result = bet.settle(state, roll)

    assert result == BetResult(bankroll_delta=0, remaining_stake=0)


def test_settle_other_number_during_point():
    """Test that other numbers during point keep bet alive."""
    state = make_state(point=6)
    bet = PassLine(stake=10)
    roll = Roll((2, 3))  # 5

    result = bet.settle(state, roll)

    assert result == BetResult(bankroll_delta=0, remaining_stake=10)


# Tests for validate() method

@pytest.mark.parametrize("stake,bankroll,table_min,table_max,point,current_bet,error_msg", [
    (-10, 1000, 5, 1000, None, 0, "negative"),
    (200, 100, 5, 1000, None, 0, "exceeds bankroll"),
    (3, 1000, 5, 1000, None, 0, "table minimum"),
    (2000, 10000, 5, 1000, None, 0, "table maximum"),
    (20, 1000, 5, 1000, 6, 10, "Cannot change"),
])
def test_validate_illegal_bets(stake, bankroll, table_min, table_max, point, current_bet, error_msg):
    """Test that illegal bets raise IllegalAction."""
    state = make_state(
        bankroll=bankroll,
        point=point,
        pass_line_bet=current_bet,
        table_min=table_min,
        table_max=table_max
    )
    bet = PassLine(stake=stake)

    with pytest.raises(InsufficientFunds, match=error_msg):
        bet.validate(state)


def test_validate_legal_bet():
    """Test that legal bets pass validation."""
    state = make_state(bankroll=1000, point=None)
    bet = PassLine(stake=10)

    bet.validate(state)  # Should not raise
