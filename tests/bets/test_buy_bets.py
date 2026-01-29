import pytest
from craps.bets.buy_bets import Buy4, Buy5, Buy6, Buy8, Buy9, Buy10
from craps.bets.model import BetResult
from craps.dice import Roll
from craps.exceptions import InsufficientFunds
from conftest import make_state


# Helper to get correct bet class by number
BUY_CLASSES = {4: Buy4, 5: Buy5, 6: Buy6, 8: Buy8, 9: Buy9, 10: Buy10}


# Tests for settle() method

@pytest.mark.parametrize("number,dice,stake,expected_winnings,expected_commission", [
    # 4/10 pays 2:1, $20 bet wins $40, commission $1
    (4, (1, 3), 20, 40, 1),
    (4, (2, 2), 20, 40, 1),
    (10, (4, 6), 20, 40, 1),
    (10, (5, 5), 20, 40, 1),

    # 5/9 pays 3:2, $20 bet wins $30, commission $1
    (5, (1, 4), 20, 30, 1),
    (5, (2, 3), 20, 30, 1),
    (9, (3, 6), 20, 30, 1),
    (9, (4, 5), 20, 30, 1),

    # 6/8 pays 6:5, $20 bet wins $24, commission $1
    (6, (1, 5), 20, 24, 1),
    (6, (2, 4), 20, 24, 1),
    (6, (3, 3), 20, 24, 1),
    (8, (2, 6), 20, 24, 1),
    (8, (3, 5), 20, 24, 1),
    (8, (4, 4), 20, 24, 1),
])
def test_buy_bet_wins_with_commission(number, dice, stake, expected_winnings, expected_commission):
    """Test that buy bet wins with correct payout minus commission."""
    state = make_state(bankroll=1000, point=4)  # Point established
    bet = BUY_CLASSES[number](stake=stake)
    roll = Roll(dice)

    result = bet.settle(state, roll)

    # bankroll_delta = winnings - commission (stake stays on table)
    assert result.bankroll_delta == expected_winnings - expected_commission
    assert result.remaining_stake == stake  # Stays on table


@pytest.mark.parametrize("number", [4, 5, 6, 8, 9, 10])
def test_buy_bet_loses_on_seven(number):
    """Test that buy bet loses on seven-out."""
    state = make_state(bankroll=1000, point=4)
    bet = BUY_CLASSES[number](stake=20)
    roll = Roll((3, 4))  # 7

    result = bet.settle(state, roll)

    assert result.bankroll_delta == 0
    assert result.remaining_stake == 0


@pytest.mark.parametrize("number,other_roll", [
    (4, Roll((2, 3))),   # 5
    (5, Roll((3, 3))),   # 6
    (6, Roll((2, 2))),   # 4
    (8, Roll((4, 6))),   # 10
    (9, Roll((1, 1))),   # 2
    (10, Roll((6, 6))),  # 12
])
def test_buy_bet_stays_on_other_numbers(number, other_roll):
    """Test that buy bet has no action on other numbers."""
    state = make_state(bankroll=1000, point=4)
    bet = BUY_CLASSES[number](stake=20)

    result = bet.settle(state, other_roll)

    assert result.bankroll_delta == 0
    assert result.remaining_stake == 20


@pytest.mark.parametrize("number,dice", [
    (4, (2, 2)),
    (5, (2, 3)),
    (6, (3, 3)),
    (8, (4, 4)),
    (9, (4, 5)),
    (10, (5, 5)),
])
def test_buy_bet_off_during_comeout(number, dice):
    """Test that buy bet is OFF during come-out roll."""
    state = make_state(bankroll=1000, point=None)  # Come-out
    bet = BUY_CLASSES[number](stake=20)
    roll = Roll(dice)

    result = bet.settle(state, roll)

    # Should have no action (not win)
    assert result.bankroll_delta == 0
    assert result.remaining_stake == 20  # Stays on table


@pytest.mark.parametrize("number", [4, 5, 6, 8, 9, 10])
def test_buy_bet_off_on_comeout_seven(number):
    """Test that buy bet doesn't lose on seven during come-out."""
    state = make_state(bankroll=1000, point=None)  # Come-out
    bet = BUY_CLASSES[number](stake=20)
    roll = Roll((3, 4))  # 7

    result = bet.settle(state, roll)

    # Should have no action (not lose)
    assert result.bankroll_delta == 0
    assert result.remaining_stake == 20  # Stays on table


def test_buy_bet_zero_stake():
    """Test that zero stake returns zero result."""
    state = make_state(bankroll=1000, point=4)
    bet = Buy6(stake=0)
    roll = Roll((3, 3))

    result = bet.settle(state, roll)

    assert result.bankroll_delta == 0
    assert result.remaining_stake == 0


# Tests for validate() method

@pytest.mark.parametrize("number", [4, 10])
def test_validate_legal_bet_4_10(number):
    """Test that legal buy bets on 4/10 pass validation (any amount)."""
    state = make_state(bankroll=1000, point=4)
    bet = BUY_CLASSES[number](stake=20)

    bet.validate(state)  # Should not raise


@pytest.mark.parametrize("number", [5, 9])
def test_validate_legal_bet_5_9(number):
    """Test that legal buy bets on 5/9 pass validation (even amounts)."""
    state = make_state(bankroll=1000, point=4)
    bet = BUY_CLASSES[number](stake=20)

    bet.validate(state)  # Even amount, should not raise


@pytest.mark.parametrize("number", [6, 8])
def test_validate_legal_bet_6_8(number):
    """Test that legal buy bets on 6/8 pass validation (multiples of 5)."""
    state = make_state(bankroll=1000, point=4)
    bet = BUY_CLASSES[number](stake=20)

    bet.validate(state)  # Multiple of 5, should not raise


@pytest.mark.parametrize("number", [4, 5, 6, 8, 9, 10])
def test_validate_negative_bet(number):
    """Test that negative buy bet raises IllegalAction."""
    state = make_state(bankroll=1000, point=4)
    bet = BUY_CLASSES[number](stake=-10)

    with pytest.raises(InsufficientFunds, match="cannot be negative"):
        bet.validate(state)


@pytest.mark.parametrize("number", [4, 5, 6, 8, 9, 10])
def test_validate_exceeds_bankroll(number):
    """Test that buy bet exceeding bankroll raises IllegalAction."""
    state = make_state(bankroll=50, point=4)
    bet = BUY_CLASSES[number](stake=100)

    with pytest.raises(InsufficientFunds, match="exceeds bankroll"):
        bet.validate(state)


@pytest.mark.parametrize("number", [4, 5, 6, 8, 9, 10])
def test_validate_below_table_min(number):
    """Test that buy bet below table min raises IllegalAction."""
    state = make_state(bankroll=1000, point=4, table_min=10)
    bet = BUY_CLASSES[number](stake=5)

    with pytest.raises(InsufficientFunds, match="table minimum"):
        bet.validate(state)


@pytest.mark.parametrize("number", [4, 5, 6, 8, 9, 10])
def test_validate_above_table_max(number):
    """Test that buy bet above table max raises IllegalAction."""
    state = make_state(bankroll=10000, point=4, table_max=500)
    bet = BUY_CLASSES[number](stake=1000)

    with pytest.raises(InsufficientFunds, match="table maximum"):
        bet.validate(state)


@pytest.mark.parametrize("number", [4, 5, 6, 8, 9, 10])
def test_validate_zero_stake(number):
    """Test that zero stake passes validation."""
    state = make_state(bankroll=1000, point=4)
    bet = BUY_CLASSES[number](stake=0)

    bet.validate(state)  # Should not raise


# Tests for increment validation

@pytest.mark.parametrize("number,valid_amount", [
    (5, 10),
    (5, 20),
    (5, 100),
    (9, 10),
    (9, 20),
    (9, 100),
])
def test_buy_5_9_even_amounts_valid(number, valid_amount):
    """Test that even amounts are valid for buy bets on 5/9 (3:2 payout)."""
    state = make_state(bankroll=1000, point=6)
    bet = BUY_CLASSES[number](stake=valid_amount)

    bet.validate(state)  # Should not raise


@pytest.mark.parametrize("number,invalid_amount", [
    (5, 11),
    (5, 15),
    (5, 99),
    (9, 11),
    (9, 15),
    (9, 99),
])
def test_buy_5_9_odd_amounts_invalid(number, invalid_amount):
    """Test that odd amounts raise IllegalAction for buy bets on 5/9."""
    state = make_state(bankroll=1000, point=6)
    bet = BUY_CLASSES[number](stake=invalid_amount)

    with pytest.raises(InsufficientFunds, match="must be even amounts"):
        bet.validate(state)


@pytest.mark.parametrize("number,valid_amount", [
    (6, 5),
    (6, 10),
    (6, 25),
    (6, 100),
    (8, 5),
    (8, 10),
    (8, 25),
    (8, 100),
])
def test_buy_6_8_multiples_of_5_valid(number, valid_amount):
    """Test that multiples of $5 are valid for buy bets on 6/8 (6:5 payout)."""
    state = make_state(bankroll=1000, point=4)
    bet = BUY_CLASSES[number](stake=valid_amount)

    bet.validate(state)  # Should not raise


@pytest.mark.parametrize("number,invalid_amount", [
    (6, 6),
    (6, 11),
    (6, 13),
    (6, 99),
    (8, 6),
    (8, 11),
    (8, 13),
    (8, 99),
])
def test_buy_6_8_non_multiples_of_5_invalid(number, invalid_amount):
    """Test that non-multiples of $5 raise IllegalAction for buy bets on 6/8."""
    state = make_state(bankroll=1000, point=4)
    bet = BUY_CLASSES[number](stake=invalid_amount)

    with pytest.raises(InsufficientFunds, match="multiples of \\$5"):
        bet.validate(state)


@pytest.mark.parametrize("number", [4, 10])
def test_buy_4_10_any_amount_valid(number):
    """Test that any amount is valid for buy bets on 4/10 (2:1 payout)."""
    state = make_state(bankroll=1000, point=6)

    # All these should be valid (no increment restrictions for 4/10)
    for amount in [7, 11, 13, 99]:
        bet = BUY_CLASSES[number](stake=amount)
        bet.validate(state)


# Payout verification tests

def test_buy_4_10_payout():
    """Test that buy bet on 4/10 pays 2:1 minus commission."""
    state = make_state(bankroll=1000, point=6)
    bet = Buy4(stake=20)
    roll = Roll((2, 2))  # 4

    result = bet.settle(state, roll)

    # $20 bet wins $40 (2:1), commission $1
    # bankroll_delta = $40 - $1 = $39
    assert result.bankroll_delta == 39
    assert result.remaining_stake == 20


def test_buy_5_9_payout():
    """Test that buy bet on 5/9 pays 3:2 minus commission."""
    state = make_state(bankroll=1000, point=6)
    bet = Buy5(stake=20)
    roll = Roll((2, 3))  # 5

    result = bet.settle(state, roll)

    # $20 bet wins $30 (3:2), commission $1
    # bankroll_delta = $30 - $1 = $29
    assert result.bankroll_delta == 29
    assert result.remaining_stake == 20


def test_buy_6_8_payout():
    """Test that buy bet on 6/8 pays 6:5 minus commission."""
    state = make_state(bankroll=1000, point=4)
    bet = Buy6(stake=20)
    roll = Roll((3, 3))  # 6

    result = bet.settle(state, roll)

    # $20 bet wins $24 (6:5), commission $1
    # bankroll_delta = $24 - $1 = $23
    assert result.bankroll_delta == 23
    assert result.remaining_stake == 20


# Commission edge cases

def test_commission_rounds_up():
    """Test that commission rounds up to nearest dollar."""
    state = make_state(bankroll=1000, point=6)
    bet = Buy4(stake=15)
    roll = Roll((2, 2))  # 4

    # $15 bet: commission = ceil($15 * 0.05) = ceil($0.75) = $1
    result = bet.settle(state, roll)

    # $15 bet wins $30 (2:1), commission $1
    # bankroll_delta = $30 - $1 = $29
    assert result.bankroll_delta == 29


def test_small_bet_commission():
    """Test that small bets pay minimum $1 commission (expensive!)."""
    state = make_state(bankroll=1000, point=6, table_min=1)
    bet = Buy4(stake=1)
    roll = Roll((2, 2))  # 4

    # $1 bet: commission = ceil($1 * 0.05) = ceil($0.05) = $1
    result = bet.settle(state, roll)

    # $1 bet wins $2 (2:1), commission $1
    # bankroll_delta = $2 - $1 = $1 (100% commission rate!)
    assert result.bankroll_delta == 1
