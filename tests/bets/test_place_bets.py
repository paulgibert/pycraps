import pytest
from craps.bets.place_bets import PlaceBet
from craps.bets.protocol import BetResult
from craps.dice import Roll
from craps.exceptions import IllegalAction
from conftest import make_state


# Tests for settle() method

@pytest.mark.parametrize("number,dice,expected_payout", [
    # 4/10 pays 9:5 ($5 bet wins $9)
    (4, (1, 3), 5 + 9),   # Stake + winnings
    (4, (2, 2), 5 + 9),
    (10, (4, 6), 5 + 9),
    (10, (5, 5), 5 + 9),

    # 5/9 pays 7:5 ($5 bet wins $7)
    (5, (1, 4), 5 + 7),
    (5, (2, 3), 5 + 7),
    (9, (3, 6), 5 + 7),
    (9, (4, 5), 5 + 7),

    # 6/8 pays 7:6 ($6 bet wins $7)
    (6, (1, 5), 6 + 7),
    (6, (2, 4), 6 + 7),
    (6, (3, 3), 6 + 7),
    (8, (2, 6), 6 + 7),
    (8, (3, 5), 6 + 7),
    (8, (4, 4), 6 + 7),
])
def test_place_bet_wins_on_number(number, dice, expected_payout):
    """Test that place bet wins with correct payout when number is rolled."""
    state = make_state(bankroll=1000, point=4)  # Point established
    bet = PlaceBet(number)
    stake = 5 if number in (4, 5, 9, 10) else 6  # Use valid increments
    roll = Roll(dice)

    result = bet.settle(state, stake, roll)

    assert result.bankroll_delta == expected_payout
    assert result.remaining_stake == stake  # Stays on table


@pytest.mark.parametrize("number", [4, 5, 6, 8, 9, 10])
def test_place_bet_loses_on_seven(number):
    """Test that place bet loses on seven-out."""
    state = make_state(bankroll=1000, point=4)
    bet = PlaceBet(number)
    roll = Roll((3, 4))  # 7

    result = bet.settle(state, 10, roll)

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
def test_place_bet_stays_on_other_numbers(number, other_roll):
    """Test that place bet has no action on other numbers."""
    state = make_state(bankroll=1000, point=4)
    bet = PlaceBet(number)
    stake = 5 if number in (4, 5, 9, 10) else 6

    result = bet.settle(state, stake, other_roll)

    assert result.bankroll_delta == 0
    assert result.remaining_stake == stake


@pytest.mark.parametrize("number,dice", [
    (4, (2, 2)),
    (5, (2, 3)),
    (6, (3, 3)),
    (8, (4, 4)),
    (9, (4, 5)),
    (10, (5, 5)),
])
def test_place_bet_off_during_comeout(number, dice):
    """Test that place bet is OFF during come-out roll."""
    state = make_state(bankroll=1000, point=None)  # Come-out
    bet = PlaceBet(number)
    stake = 5 if number in (4, 5, 9, 10) else 6
    roll = Roll(dice)

    result = bet.settle(state, stake, roll)

    # Should have no action (not win)
    assert result.bankroll_delta == 0
    assert result.remaining_stake == stake  # Stays on table


@pytest.mark.parametrize("number", [4, 5, 6, 8, 9, 10])
def test_place_bet_off_on_comeout_seven(number):
    """Test that place bet doesn't lose on seven during come-out."""
    state = make_state(bankroll=1000, point=None)  # Come-out
    bet = PlaceBet(number)
    stake = 5 if number in (4, 5, 9, 10) else 6
    roll = Roll((3, 4))  # 7

    result = bet.settle(state, stake, roll)

    # Should have no action (not lose)
    assert result.bankroll_delta == 0
    assert result.remaining_stake == stake  # Stays on table


def test_place_bet_zero_stake():
    """Test that zero stake returns zero result."""
    state = make_state(bankroll=1000, point=4)
    bet = PlaceBet(6)
    roll = Roll((3, 3))

    result = bet.settle(state, 0, roll)

    assert result.bankroll_delta == 0
    assert result.remaining_stake == 0


# Tests for validate() method

@pytest.mark.parametrize("number", [4, 5, 6, 8, 9, 10])
def test_validate_legal_bet(number):
    """Test that legal place bets pass validation."""
    state = make_state(bankroll=1000, point=4)
    bet = PlaceBet(number)
    stake = 5 if number in (4, 5, 9, 10) else 6

    bet.validate(state, stake)  # Should not raise


@pytest.mark.parametrize("number", [4, 5, 6, 8, 9, 10])
def test_validate_negative_bet(number):
    """Test that negative place bet raises IllegalAction."""
    state = make_state(bankroll=1000, point=4)
    bet = PlaceBet(number)

    with pytest.raises(IllegalAction, match="cannot be negative"):
        bet.validate(state, -10)


@pytest.mark.parametrize("number", [4, 5, 6, 8, 9, 10])
def test_validate_exceeds_bankroll(number):
    """Test that place bet exceeding bankroll raises IllegalAction."""
    state = make_state(bankroll=50, point=4)
    bet = PlaceBet(number)

    with pytest.raises(IllegalAction, match="exceeds bankroll"):
        bet.validate(state, 100)


@pytest.mark.parametrize("number", [4, 5, 6, 8, 9, 10])
def test_validate_below_table_min(number):
    """Test that place bet below table min raises IllegalAction."""
    state = make_state(bankroll=1000, point=4, table_min=10)
    bet = PlaceBet(number)

    with pytest.raises(IllegalAction, match="table minimum"):
        bet.validate(state, 5)


@pytest.mark.parametrize("number", [4, 5, 6, 8, 9, 10])
def test_validate_above_table_max(number):
    """Test that place bet above table max raises IllegalAction."""
    state = make_state(bankroll=10000, point=4, table_max=500)
    bet = PlaceBet(number)

    with pytest.raises(IllegalAction, match="table maximum"):
        bet.validate(state, 1000)


@pytest.mark.parametrize("number", [4, 5, 6, 8, 9, 10])
def test_validate_zero_stake(number):
    """Test that zero stake passes validation."""
    state = make_state(bankroll=1000, point=4)
    bet = PlaceBet(number)

    bet.validate(state, 0)  # Should not raise


# Tests for increment validation

@pytest.mark.parametrize("number,valid_amount", [
    (6, 6),
    (6, 12),
    (6, 18),
    (6, 60),
    (8, 6),
    (8, 12),
    (8, 18),
    (8, 60),
])
def test_place_6_8_multiples_of_6_valid(number, valid_amount):
    """Test that multiples of $6 are valid for place bets on 6/8."""
    state = make_state(bankroll=1000, point=4)
    bet = PlaceBet(number)

    bet.validate(state, valid_amount)  # Should not raise


@pytest.mark.parametrize("number,invalid_amount", [
    (6, 5),
    (6, 7),
    (6, 11),
    (6, 13),
    (8, 5),
    (8, 7),
    (8, 11),
    (8, 13),
])
def test_place_6_8_non_multiples_of_6_invalid(number, invalid_amount):
    """Test that non-multiples of $6 raise IllegalAction for place bets on 6/8."""
    state = make_state(bankroll=1000, point=4)
    bet = PlaceBet(number)

    with pytest.raises(IllegalAction, match="multiples of \\$6"):
        bet.validate(state, invalid_amount)


@pytest.mark.parametrize("number,valid_amount", [
    (5, 5),
    (5, 10),
    (5, 15),
    (5, 100),
    (9, 5),
    (9, 10),
    (9, 15),
    (9, 100),
    (4, 5),
    (4, 10),
    (4, 15),
    (4, 100),
    (10, 5),
    (10, 10),
    (10, 15),
    (10, 100),
])
def test_place_4_5_9_10_multiples_of_5_valid(number, valid_amount):
    """Test that multiples of $5 are valid for place bets on 4/5/9/10."""
    state = make_state(bankroll=1000, point=6)
    bet = PlaceBet(number)

    bet.validate(state, valid_amount)  # Should not raise


@pytest.mark.parametrize("number,invalid_amount", [
    (5, 6),
    (5, 11),
    (5, 13),
    (9, 6),
    (9, 11),
    (9, 13),
    (4, 6),
    (4, 11),
    (4, 13),
    (10, 6),
    (10, 11),
    (10, 13),
])
def test_place_4_5_9_10_non_multiples_of_5_invalid(number, invalid_amount):
    """Test that non-multiples of $5 raise IllegalAction for place bets on 4/5/9/10."""
    state = make_state(bankroll=1000, point=6)
    bet = PlaceBet(number)

    with pytest.raises(IllegalAction, match="multiples of \\$5"):
        bet.validate(state, invalid_amount)


# Payout verification tests

def test_place_4_10_payout():
    """Test that place bet on 4/10 pays 9:5."""
    state = make_state(bankroll=1000, point=6)
    bet = PlaceBet(4)
    roll = Roll((2, 2))  # 4

    result = bet.settle(state, 5, roll)

    assert result.bankroll_delta == 14  # $5 stake + $9 winnings


def test_place_5_9_payout():
    """Test that place bet on 5/9 pays 7:5."""
    state = make_state(bankroll=1000, point=6)
    bet = PlaceBet(5)
    roll = Roll((2, 3))  # 5

    result = bet.settle(state, 5, roll)

    assert result.bankroll_delta == 12  # $5 stake + $7 winnings


def test_place_6_8_payout():
    """Test that place bet on 6/8 pays 7:6."""
    state = make_state(bankroll=1000, point=4)
    bet = PlaceBet(6)
    roll = Roll((3, 3))  # 6

    result = bet.settle(state, 6, roll)

    assert result.bankroll_delta == 13  # $6 stake + $7 winnings


# Edge case tests

def test_invalid_place_number():
    """Test that invalid place number raises ValueError."""
    with pytest.raises(ValueError, match="Invalid place number"):
        PlaceBet(7)

    with pytest.raises(ValueError, match="Invalid place number"):
        PlaceBet(11)
