import pytest
from craps.bets.field_bet import FieldBet
from craps.bets.model import BetResult
from craps.dice import Roll
from craps.exceptions import InsufficientFunds
from conftest import make_state


# Tests for settle() method

def test_field_wins_on_2_pays_2_to_1():
    """Test that field bet on 2 pays 2:1."""
    state = make_state(bankroll=1000, point=None)
    bet = FieldBet(stake=10)
    roll = Roll((1, 1))  # 2

    result = bet.settle(state, roll)

    # Pays 2:1: stake + 2x stake = $10 + $20 = $30
    assert result.bankroll_delta == 30
    assert result.remaining_stake == 0  # One-roll bet


def test_field_wins_on_12_pays_3_to_1():
    """Test that field bet on 12 pays 3:1."""
    state = make_state(bankroll=1000, point=None)
    bet = FieldBet(stake=10)
    roll = Roll((6, 6))  # 12

    result = bet.settle(state, roll)

    # Pays 3:1: stake + 3x stake = $10 + $30 = $40
    assert result.bankroll_delta == 40
    assert result.remaining_stake == 0  # One-roll bet


@pytest.mark.parametrize("dice", [
    (1, 2),  # 3
    (1, 3),  # 4
    (3, 6),  # 9
    (4, 6),  # 10
    (5, 6),  # 11
])
def test_field_wins_on_other_numbers_pays_1_to_1(dice):
    """Test that field bet on 3, 4, 9, 10, 11 pays 1:1."""
    state = make_state(bankroll=1000, point=None)
    bet = FieldBet(stake=10)
    roll = Roll(dice)

    result = bet.settle(state, roll)

    # Pays 1:1: stake + stake = $10 + $10 = $20
    assert result.bankroll_delta == 20
    assert result.remaining_stake == 0  # One-roll bet


@pytest.mark.parametrize("dice", [
    (1, 4),  # 5
    (1, 5),  # 6
    (3, 4),  # 7
    (2, 6),  # 8
])
def test_field_loses_on_5_6_7_8(dice):
    """Test that field bet loses on 5, 6, 7, 8."""
    state = make_state(bankroll=1000, point=None)
    bet = FieldBet(stake=10)
    roll = Roll(dice)

    result = bet.settle(state, roll)

    assert result.bankroll_delta == 0
    assert result.remaining_stake == 0  # One-roll bet


def test_field_works_during_come_out():
    """Test that field bet works during come-out roll."""
    state = make_state(bankroll=1000, point=None)  # Come-out
    bet = FieldBet(stake=10)
    roll = Roll((1, 1))  # 2

    result = bet.settle(state, roll)

    # Should win (always ON)
    assert result.bankroll_delta == 30


def test_field_works_during_point():
    """Test that field bet works during point phase."""
    state = make_state(bankroll=1000, point=6)  # Point established
    bet = FieldBet(stake=10)
    roll = Roll((1, 1))  # 2

    result = bet.settle(state, roll)

    # Should win (always ON)
    assert result.bankroll_delta == 30


def test_field_zero_stake():
    """Test that zero stake returns zero result."""
    state = make_state(bankroll=1000, point=None)
    bet = FieldBet(stake=0)
    roll = Roll((1, 1))

    result = bet.settle(state, roll)

    assert result.bankroll_delta == 0
    assert result.remaining_stake == 0


# Tests for validate() method

def test_validate_legal_bet():
    """Test that legal field bet passes validation."""
    state = make_state(bankroll=1000, point=None)
    bet = FieldBet(stake=10)

    bet.validate(state)  # Should not raise


def test_validate_negative_bet():
    """Test that negative field bet raises IllegalAction."""
    state = make_state(bankroll=1000, point=None)
    bet = FieldBet(stake=-10)

    with pytest.raises(InsufficientFunds, match="cannot be negative"):
        bet.validate(state)


def test_validate_exceeds_bankroll():
    """Test that field bet exceeding bankroll raises IllegalAction."""
    state = make_state(bankroll=50, point=None)
    bet = FieldBet(stake=100)

    with pytest.raises(InsufficientFunds, match="exceeds bankroll"):
        bet.validate(state)


def test_validate_below_table_min():
    """Test that field bet below table min raises IllegalAction."""
    state = make_state(bankroll=1000, point=None, table_min=10)
    bet = FieldBet(stake=5)

    with pytest.raises(InsufficientFunds, match="table minimum"):
        bet.validate(state)


def test_validate_above_table_max():
    """Test that field bet above table max raises IllegalAction."""
    state = make_state(bankroll=10000, point=None, table_max=500)
    bet = FieldBet(stake=1000)

    with pytest.raises(InsufficientFunds, match="table maximum"):
        bet.validate(state)


def test_validate_zero_stake():
    """Test that zero stake passes validation."""
    state = make_state(bankroll=1000, point=None)
    bet = FieldBet(stake=0)

    bet.validate(state)  # Should not raise


# Comprehensive payout verification

@pytest.mark.parametrize("dice,expected_payout", [
    ((1, 1), 30),   # 2 pays 2:1
    ((1, 2), 20),   # 3 pays 1:1
    ((1, 3), 20),   # 4 pays 1:1
    ((2, 2), 20),   # 4 pays 1:1
    ((3, 6), 20),   # 9 pays 1:1
    ((4, 5), 20),   # 9 pays 1:1
    ((4, 6), 20),   # 10 pays 1:1
    ((5, 5), 20),   # 10 pays 1:1
    ((5, 6), 20),   # 11 pays 1:1
    ((6, 6), 40),   # 12 pays 3:1
])
def test_all_winning_numbers(dice, expected_payout):
    """Test that all winning numbers pay correctly."""
    state = make_state(bankroll=1000, point=None)
    bet = FieldBet(stake=10)

    result = bet.settle(state, Roll(dice))

    assert result.bankroll_delta == expected_payout
    assert result.remaining_stake == 0


@pytest.mark.parametrize("dice", [
    (1, 4),  # 5
    (2, 3),  # 5
    (1, 5),  # 6
    (2, 4),  # 6
    (3, 3),  # 6
    (1, 6),  # 7
    (2, 5),  # 7
    (3, 4),  # 7
    (2, 6),  # 8
    (3, 5),  # 8
    (4, 4),  # 8
])
def test_all_losing_numbers(dice):
    """Test that all losing numbers lose correctly."""
    state = make_state(bankroll=1000, point=None)
    bet = FieldBet(stake=10)

    result = bet.settle(state, Roll(dice))

    assert result.bankroll_delta == 0
    assert result.remaining_stake == 0
