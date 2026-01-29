import pytest
from craps.bets.come_odds import ComeOdds4, ComeOdds5, ComeOdds6, ComeOdds8, ComeOdds9, ComeOdds10
from craps.dice import Roll
from craps.exceptions import InsufficientFunds
from conftest import make_state


# Helper to get correct bet class by come point
COME_ODDS_CLASSES = {
    4: ComeOdds4, 5: ComeOdds5, 6: ComeOdds6,
    8: ComeOdds8, 9: ComeOdds9, 10: ComeOdds10
}


# Tests for settle() method

@pytest.mark.parametrize("come_point,roll,expected_payout", [
    # Point 4 wins with 2:1 odds
    (4, Roll((2, 2)), 30),  # $10 odds -> $10 + $20 win
    (4, Roll((1, 3)), 30),

    # Point 10 wins with 2:1 odds
    (10, Roll((5, 5)), 30),
    (10, Roll((4, 6)), 30),

    # Point 5 wins with 3:2 odds
    (5, Roll((2, 3)), 25),  # $10 odds -> $10 + $15 win
    (5, Roll((1, 4)), 25),

    # Point 9 wins with 3:2 odds
    (9, Roll((4, 5)), 25),
    (9, Roll((3, 6)), 25),

    # Point 6 wins with 6:5 odds
    (6, Roll((3, 3)), 22),  # $10 odds -> $10 + $12 win
    (6, Roll((2, 4)), 22),

    # Point 8 wins with 6:5 odds
    (8, Roll((4, 4)), 22),
    (8, Roll((3, 5)), 22),
])
def test_come_odds_win(come_point, roll, expected_payout):
    """Test that come odds wins when the come point is hit."""
    state = make_state(bankroll=1000, point=6, **{f'come_{come_point}': 10})
    bet = COME_ODDS_CLASSES[come_point](stake=10)

    result = bet.settle(state, roll)

    assert result.bankroll_delta == expected_payout
    assert result.remaining_stake == 0


@pytest.mark.parametrize("come_point", [4, 5, 6, 8, 9, 10])
def test_come_odds_seven_out(come_point):
    """Test that come odds loses on seven-out."""
    state = make_state(bankroll=1000, point=6, **{f'come_{come_point}': 10})
    bet = COME_ODDS_CLASSES[come_point](stake=10)
    roll = Roll((3, 4))  # 7

    result = bet.settle(state, roll)

    assert result.bankroll_delta == 0
    assert result.remaining_stake == 0


@pytest.mark.parametrize("come_point,other_roll", [
    (4, Roll((2, 3))),   # 5
    (5, Roll((3, 3))),   # 6
    (6, Roll((2, 2))),   # 4
    (8, Roll((4, 6))),   # 10
    (9, Roll((1, 1))),   # 2
    (10, Roll((6, 6))),  # 12
])
def test_come_odds_stays(come_point, other_roll):
    """Test that come odds stays on other rolls."""
    state = make_state(bankroll=1000, point=6, **{f'come_{come_point}': 10})
    bet = COME_ODDS_CLASSES[come_point](stake=10)

    result = bet.settle(state, other_roll)

    assert result.bankroll_delta == 0
    assert result.remaining_stake == 10


def test_come_odds_zero_stake():
    """Test that zero stake returns zero result."""
    state = make_state(bankroll=1000, point=6, come_4=10)
    bet = ComeOdds4(stake=0)
    roll = Roll((2, 2))

    result = bet.settle(state, roll)

    assert result.bankroll_delta == 0
    assert result.remaining_stake == 0


# Tests for validate() method

@pytest.mark.parametrize("come_point", [4, 5, 6, 8, 9, 10])
def test_valid_come_odds(come_point):
    """Test that valid come odds passes validation."""
    state = make_state(bankroll=1000, point=6, **{f'come_{come_point}': 10})
    bet = COME_ODDS_CLASSES[come_point](stake=10)

    # Should not raise
    bet.validate(state)


def test_come_odds_negative():
    """Test that negative odds raises IllegalAction."""
    state = make_state(bankroll=1000, point=6, come_4=10)
    bet = ComeOdds4(stake=-10)

    with pytest.raises(InsufficientFunds, match="cannot be negative"):
        bet.validate(state)


@pytest.mark.parametrize("come_point", [4, 5, 6, 8, 9, 10])
def test_come_odds_no_come_bet(come_point):
    """Test that odds without come bet raises IllegalAction."""
    state = make_state(bankroll=1000, point=6)
    bet = COME_ODDS_CLASSES[come_point](stake=10)

    with pytest.raises(InsufficientFunds, match="without an established come bet"):
        bet.validate(state)


def test_come_odds_exceeds_max_odds():
    """Test that odds exceeding max_odds raises IllegalAction."""
    state = make_state(bankroll=1000, point=6, come_4=10, max_odds=3)
    bet = ComeOdds4(stake=40)  # 4x the come bet

    with pytest.raises(InsufficientFunds, match="3x"):
        bet.validate(state)


def test_come_odds_exceeds_bankroll():
    """Test that odds exceeding bankroll raises IllegalAction."""
    state = make_state(bankroll=50, point=6, come_4=10)
    bet = ComeOdds4(stake=100)

    with pytest.raises(InsufficientFunds, match="exceeds bankroll"):
        bet.validate(state)


# Tests for increment validation

@pytest.mark.parametrize("come_point,valid_amount", [
    (5, 10),   # Even amount
    (5, 20),
    (5, 100),
    (9, 10),
    (9, 20),
    (9, 100),
])
def test_come_odds_5_9_even_amounts_valid(come_point, valid_amount):
    """Test that even amounts are valid for come odds on 5/9."""
    state = make_state(bankroll=1000, point=6, max_odds=20, **{f'come_{come_point}': 10})
    bet = COME_ODDS_CLASSES[come_point](stake=valid_amount)

    # Should not raise
    bet.validate(state)


@pytest.mark.parametrize("come_point,invalid_amount", [
    (5, 11),   # Odd amount
    (5, 15),
    (5, 99),
    (9, 11),
    (9, 15),
    (9, 99),
])
def test_come_odds_5_9_odd_amounts_invalid(come_point, invalid_amount):
    """Test that odd amounts raise IllegalAction for come odds on 5/9."""
    state = make_state(bankroll=1000, point=6, max_odds=20, **{f'come_{come_point}': 10})
    bet = COME_ODDS_CLASSES[come_point](stake=invalid_amount)

    with pytest.raises(InsufficientFunds, match="must be even amounts"):
        bet.validate(state)


@pytest.mark.parametrize("come_point,valid_amount", [
    (6, 5),
    (6, 10),
    (6, 25),
    (6, 100),
    (8, 5),
    (8, 10),
    (8, 25),
    (8, 100),
])
def test_come_odds_6_8_multiples_of_5_valid(come_point, valid_amount):
    """Test that multiples of $5 are valid for come odds on 6/8."""
    state = make_state(bankroll=1000, point=6, max_odds=20, **{f'come_{come_point}': 10})
    bet = COME_ODDS_CLASSES[come_point](stake=valid_amount)

    # Should not raise
    bet.validate(state)


@pytest.mark.parametrize("come_point,invalid_amount", [
    (6, 11),
    (6, 13),
    (6, 99),
    (8, 11),
    (8, 13),
    (8, 99),
])
def test_come_odds_6_8_non_multiples_of_5_invalid(come_point, invalid_amount):
    """Test that non-multiples of $5 raise IllegalAction for come odds on 6/8."""
    state = make_state(bankroll=1000, point=6, max_odds=20, **{f'come_{come_point}': 10})
    bet = COME_ODDS_CLASSES[come_point](stake=invalid_amount)

    with pytest.raises(InsufficientFunds, match="must be multiples of \\$5"):
        bet.validate(state)


@pytest.mark.parametrize("come_point", [4, 10])
def test_come_odds_4_10_any_amount_valid(come_point):
    """Test that any amount is valid for come odds on 4/10 (no increment requirements)."""
    state = make_state(bankroll=1000, point=6, max_odds=20, **{f'come_{come_point}': 10})

    # All these should be valid (no increment restrictions for 4/10)
    for amount in [7, 11, 13, 99]:
        bet = COME_ODDS_CLASSES[come_point](stake=amount)
        bet.validate(state)


# Tests for edge cases

def test_come_odds_zero_stake_validation():
    """Test that zero stake always passes validation."""
    state = make_state(bankroll=1000, point=6)  # No come bet
    bet = ComeOdds4(stake=0)

    # Should not raise even without come bet
    bet.validate(state)
