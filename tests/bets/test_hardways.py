import pytest
from craps.bets.hardways import Hard4, Hard6, Hard8, Hard10
from craps.bets.model import BetResult
from craps.dice import Roll
from craps.exceptions import InsufficientFunds
from conftest import make_state


# Helper to get correct bet class by number
HARDWAY_CLASSES = {4: Hard4, 6: Hard6, 8: Hard8, 10: Hard10}


# Tests for settle() method - Hard 4

def test_hard_4_wins():
    """Test that hard 4 (2,2) wins and pays 7:1."""
    state = make_state(bankroll=1000, point=6)
    bet = Hard4(stake=10)
    roll = Roll((2, 2))  # Hard 4

    result = bet.settle(state, roll)

    # Pays 7:1: stake + 7x stake = $10 + $70 = $80
    assert result.bankroll_delta == 80
    assert result.remaining_stake == 0  # Bet resolves


def test_hard_4_loses_easy():
    """Test that hard 4 loses on easy 4."""
    state = make_state(bankroll=1000, point=6)
    bet = Hard4(stake=10)
    roll = Roll((1, 3))  # Easy 4

    result = bet.settle(state, roll)

    assert result.bankroll_delta == 0
    assert result.remaining_stake == 0


# Tests for settle() method - Hard 6

def test_hard_6_wins():
    """Test that hard 6 (3,3) wins and pays 9:1."""
    state = make_state(bankroll=1000, point=4)
    bet = Hard6(stake=10)
    roll = Roll((3, 3))  # Hard 6

    result = bet.settle(state, roll)

    # Pays 9:1: stake + 9x stake = $10 + $90 = $100
    assert result.bankroll_delta == 100
    assert result.remaining_stake == 0


@pytest.mark.parametrize("dice", [(1, 5), (2, 4)])
def test_hard_6_loses_easy(dice):
    """Test that hard 6 loses on easy 6."""
    state = make_state(bankroll=1000, point=4)
    bet = Hard6(stake=10)
    roll = Roll(dice)  # Easy 6

    result = bet.settle(state, roll)

    assert result.bankroll_delta == 0
    assert result.remaining_stake == 0


# Tests for settle() method - Hard 8

def test_hard_8_wins():
    """Test that hard 8 (4,4) wins and pays 9:1."""
    state = make_state(bankroll=1000, point=6)
    bet = Hard8(stake=10)
    roll = Roll((4, 4))  # Hard 8

    result = bet.settle(state, roll)

    # Pays 9:1
    assert result.bankroll_delta == 100
    assert result.remaining_stake == 0


@pytest.mark.parametrize("dice", [(2, 6), (3, 5)])
def test_hard_8_loses_easy(dice):
    """Test that hard 8 loses on easy 8."""
    state = make_state(bankroll=1000, point=6)
    bet = Hard8(stake=10)
    roll = Roll(dice)  # Easy 8

    result = bet.settle(state, roll)

    assert result.bankroll_delta == 0
    assert result.remaining_stake == 0


# Tests for settle() method - Hard 10

def test_hard_10_wins():
    """Test that hard 10 (5,5) wins and pays 7:1."""
    state = make_state(bankroll=1000, point=6)
    bet = Hard10(stake=10)
    roll = Roll((5, 5))  # Hard 10

    result = bet.settle(state, roll)

    # Pays 7:1
    assert result.bankroll_delta == 80
    assert result.remaining_stake == 0


def test_hard_10_loses_easy():
    """Test that hard 10 loses on easy 10."""
    state = make_state(bankroll=1000, point=6)
    bet = Hard10(stake=10)
    roll = Roll((4, 6))  # Easy 10

    result = bet.settle(state, roll)

    assert result.bankroll_delta == 0
    assert result.remaining_stake == 0


# Tests for all hardways losing on seven

@pytest.mark.parametrize("number", [4, 6, 8, 10])
def test_hardway_loses_on_seven(number):
    """Test that all hardways lose on 7."""
    state = make_state(bankroll=1000, point=6)
    bet = HARDWAY_CLASSES[number](stake=10)
    roll = Roll((3, 4))  # 7

    result = bet.settle(state, roll)

    assert result.bankroll_delta == 0
    assert result.remaining_stake == 0


# Tests for OFF during come-out

@pytest.mark.parametrize("number,dice", [
    (4, (2, 2)),
    (6, (3, 3)),
    (8, (4, 4)),
    (10, (5, 5)),
])
def test_hardway_off_during_comeout(number, dice):
    """Test that hardway bets are OFF during come-out roll."""
    state = make_state(bankroll=1000, point=None)  # Come-out
    bet = HARDWAY_CLASSES[number](stake=10)
    roll = Roll(dice)

    result = bet.settle(state, roll)

    # Should have no action (not win)
    assert result.bankroll_delta == 0
    assert result.remaining_stake == 10  # Stays on table


@pytest.mark.parametrize("number", [4, 6, 8, 10])
def test_hardway_off_on_comeout_seven(number):
    """Test that hardways don't lose on seven during come-out."""
    state = make_state(bankroll=1000, point=None)  # Come-out
    bet = HARDWAY_CLASSES[number](stake=10)
    roll = Roll((3, 4))  # 7

    result = bet.settle(state, roll)

    # Should have no action (not lose)
    assert result.bankroll_delta == 0
    assert result.remaining_stake == 10  # Stays on table


# Tests for no action on other numbers

@pytest.mark.parametrize("number,other_dice", [
    (4, (2, 3)),  # 5
    (6, (2, 2)),  # 4
    (8, (5, 5)),  # 10
    (10, (1, 1)), # 2
])
def test_hardway_stays_on_other_numbers(number, other_dice):
    """Test that hardway bet has no action on other numbers."""
    state = make_state(bankroll=1000, point=6)
    bet = HARDWAY_CLASSES[number](stake=10)
    roll = Roll(other_dice)

    result = bet.settle(state, roll)

    assert result.bankroll_delta == 0
    assert result.remaining_stake == 10  # Stays on table


def test_hardway_zero_stake():
    """Test that zero stake returns zero result."""
    state = make_state(bankroll=1000, point=6)
    bet = Hard6(stake=0)
    roll = Roll((3, 3))

    result = bet.settle(state, roll)

    assert result.bankroll_delta == 0
    assert result.remaining_stake == 0


# Tests for validate() method

@pytest.mark.parametrize("number", [4, 6, 8, 10])
def test_validate_legal_bet(number):
    """Test that legal hardway bets pass validation."""
    state = make_state(bankroll=1000, point=6, prop_min=1)
    bet = HARDWAY_CLASSES[number](stake=5)

    bet.validate(state)  # Should not raise


@pytest.mark.parametrize("number", [4, 6, 8, 10])
def test_validate_negative_bet(number):
    """Test that negative hardway bet raises IllegalAction."""
    state = make_state(bankroll=1000, point=6)
    bet = HARDWAY_CLASSES[number](stake=-10)

    with pytest.raises(InsufficientFunds, match="cannot be negative"):
        bet.validate(state)


@pytest.mark.parametrize("number", [4, 6, 8, 10])
def test_validate_exceeds_bankroll(number):
    """Test that hardway bet exceeding bankroll raises IllegalAction."""
    state = make_state(bankroll=50, point=6)
    bet = HARDWAY_CLASSES[number](stake=100)

    with pytest.raises(InsufficientFunds, match="exceeds bankroll"):
        bet.validate(state)


@pytest.mark.parametrize("number", [4, 6, 8, 10])
def test_validate_below_prop_min(number):
    """Test that hardway bet below prop min raises IllegalAction."""
    state = make_state(bankroll=1000, point=6, prop_min=5)
    bet = HARDWAY_CLASSES[number](stake=3)

    with pytest.raises(InsufficientFunds, match="prop minimum"):
        bet.validate(state)


@pytest.mark.parametrize("number", [4, 6, 8, 10])
def test_validate_above_table_max(number):
    """Test that hardway bet above table max raises IllegalAction."""
    state = make_state(bankroll=10000, point=6, table_max=500)
    bet = HARDWAY_CLASSES[number](stake=1000)

    with pytest.raises(InsufficientFunds, match="table maximum"):
        bet.validate(state)


@pytest.mark.parametrize("number", [4, 6, 8, 10])
def test_validate_zero_stake(number):
    """Test that zero stake passes validation."""
    state = make_state(bankroll=1000, point=6)
    bet = HARDWAY_CLASSES[number](stake=0)

    bet.validate(state)  # Should not raise
