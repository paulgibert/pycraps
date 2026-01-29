import pytest
from craps.bets.props import AnySeven, AnyCraps, AceDeuce, Aces, Boxcars, YoLeven, Horn, CAndE
from craps.bets.model import BetResult
from craps.dice import Roll
from craps.exceptions import InsufficientFunds
from conftest import make_state


# Tests for AnySeven

def test_any_seven_wins():
    """Test that Any Seven wins on 7 and pays 4:1."""
    state = make_state(bankroll=1000, point=None)
    bet = AnySeven(stake=10)
    roll = Roll((3, 4))  # 7

    result = bet.settle(state, roll)

    # Pays 4:1: stake + 4x stake = $10 + $40 = $50
    assert result.bankroll_delta == 50
    assert result.remaining_stake == 0  # One-roll bet


@pytest.mark.parametrize("dice", [(1, 1), (1, 2), (2, 2), (3, 3)])
def test_any_seven_loses(dice):
    """Test that Any Seven loses on non-7."""
    state = make_state(bankroll=1000, point=None)
    bet = AnySeven(stake=10)
    roll = Roll(dice)

    result = bet.settle(state, roll)

    assert result.bankroll_delta == 0
    assert result.remaining_stake == 0


# Tests for AnyCraps

@pytest.mark.parametrize("dice", [(1, 1), (1, 2), (6, 6)])
def test_any_craps_wins(dice):
    """Test that Any Craps wins on 2, 3, 12 and pays 7:1."""
    state = make_state(bankroll=1000, point=None)
    bet = AnyCraps(stake=10)
    roll = Roll(dice)

    result = bet.settle(state, roll)

    # Pays 7:1: stake + 7x stake = $10 + $70 = $80
    assert result.bankroll_delta == 80
    assert result.remaining_stake == 0


@pytest.mark.parametrize("dice", [(1, 3), (3, 4), (5, 6)])
def test_any_craps_loses(dice):
    """Test that Any Craps loses on non-craps."""
    state = make_state(bankroll=1000, point=None)
    bet = AnyCraps(stake=10)
    roll = Roll(dice)

    result = bet.settle(state, roll)

    assert result.bankroll_delta == 0
    assert result.remaining_stake == 0


# Tests for AceDeuce (3)

def test_ace_deuce_wins():
    """Test that Ace-Deuce wins on 3 and pays 15:1."""
    state = make_state(bankroll=1000, point=None)
    bet = AceDeuce(stake=10)
    roll = Roll((1, 2))  # 3

    result = bet.settle(state, roll)

    # Pays 15:1: stake + 15x stake = $10 + $150 = $160
    assert result.bankroll_delta == 160
    assert result.remaining_stake == 0


@pytest.mark.parametrize("dice", [(1, 1), (2, 2), (3, 4)])
def test_ace_deuce_loses(dice):
    """Test that Ace-Deuce loses on non-3."""
    state = make_state(bankroll=1000, point=None)
    bet = AceDeuce(stake=10)
    roll = Roll(dice)

    result = bet.settle(state, roll)

    assert result.bankroll_delta == 0
    assert result.remaining_stake == 0


# Tests for Aces (2)

def test_aces_wins():
    """Test that Aces wins on 2 and pays 30:1."""
    state = make_state(bankroll=1000, point=None)
    bet = Aces(stake=10)
    roll = Roll((1, 1))  # 2

    result = bet.settle(state, roll)

    # Pays 30:1: stake + 30x stake = $10 + $300 = $310
    assert result.bankroll_delta == 310
    assert result.remaining_stake == 0


@pytest.mark.parametrize("dice", [(1, 2), (2, 2), (3, 4)])
def test_aces_loses(dice):
    """Test that Aces loses on non-2."""
    state = make_state(bankroll=1000, point=None)
    bet = Aces(stake=10)
    roll = Roll(dice)

    result = bet.settle(state, roll)

    assert result.bankroll_delta == 0
    assert result.remaining_stake == 0


# Tests for Boxcars (12)

def test_boxcars_wins():
    """Test that Boxcars wins on 12 and pays 30:1."""
    state = make_state(bankroll=1000, point=None)
    bet = Boxcars(stake=10)
    roll = Roll((6, 6))  # 12

    result = bet.settle(state, roll)

    # Pays 30:1: stake + 30x stake = $10 + $300 = $310
    assert result.bankroll_delta == 310
    assert result.remaining_stake == 0


@pytest.mark.parametrize("dice", [(1, 1), (1, 2), (3, 4)])
def test_boxcars_loses(dice):
    """Test that Boxcars loses on non-12."""
    state = make_state(bankroll=1000, point=None)
    bet = Boxcars(stake=10)
    roll = Roll(dice)

    result = bet.settle(state, roll)

    assert result.bankroll_delta == 0
    assert result.remaining_stake == 0


# Tests for YoLeven (11)

def test_yo_leven_wins():
    """Test that Yo-leven wins on 11 and pays 15:1."""
    state = make_state(bankroll=1000, point=None)
    bet = YoLeven(stake=10)
    roll = Roll((5, 6))  # 11

    result = bet.settle(state, roll)

    # Pays 15:1: stake + 15x stake = $10 + $150 = $160
    assert result.bankroll_delta == 160
    assert result.remaining_stake == 0


@pytest.mark.parametrize("dice", [(1, 1), (1, 2), (3, 4)])
def test_yo_leven_loses(dice):
    """Test that Yo-leven loses on non-11."""
    state = make_state(bankroll=1000, point=None)
    bet = YoLeven(stake=10)
    roll = Roll(dice)

    result = bet.settle(state, roll)

    assert result.bankroll_delta == 0
    assert result.remaining_stake == 0


# Tests for Horn

def test_horn_wins_on_2():
    """Test that Horn wins on 2 (pays 30:1 on that portion)."""
    state = make_state(bankroll=1000, point=None)
    bet = Horn(stake=20)
    roll = Roll((1, 1))  # 2

    # $20 bet splits into $5 each on 2, 3, 11, 12
    # Win $5 on 2 (pays 30:1) = $5 + $150 = $155
    result = bet.settle(state, roll)

    assert result.bankroll_delta == 155
    assert result.remaining_stake == 0


def test_horn_wins_on_3():
    """Test that Horn wins on 3 (pays 15:1 on that portion)."""
    state = make_state(bankroll=1000, point=None)
    bet = Horn(stake=20)
    roll = Roll((1, 2))  # 3

    # $20 bet splits into $5 each on 2, 3, 11, 12
    # Win $5 on 3 (pays 15:1) = $5 + $75 = $80
    result = bet.settle(state, roll)

    assert result.bankroll_delta == 80
    assert result.remaining_stake == 0


def test_horn_wins_on_11():
    """Test that Horn wins on 11 (pays 15:1 on that portion)."""
    state = make_state(bankroll=1000, point=None)
    bet = Horn(stake=20)
    roll = Roll((5, 6))  # 11

    # $20 bet splits into $5 each on 2, 3, 11, 12
    # Win $5 on 11 (pays 15:1) = $5 + $75 = $80
    result = bet.settle(state, roll)

    assert result.bankroll_delta == 80
    assert result.remaining_stake == 0


def test_horn_wins_on_12():
    """Test that Horn wins on 12 (pays 30:1 on that portion)."""
    state = make_state(bankroll=1000, point=None)
    bet = Horn(stake=20)
    roll = Roll((6, 6))  # 12

    # $20 bet splits into $5 each on 2, 3, 11, 12
    # Win $5 on 12 (pays 30:1) = $5 + $150 = $155
    result = bet.settle(state, roll)

    assert result.bankroll_delta == 155
    assert result.remaining_stake == 0


@pytest.mark.parametrize("dice", [(1, 3), (3, 4), (2, 2)])
def test_horn_loses(dice):
    """Test that Horn loses on non-horn numbers."""
    state = make_state(bankroll=1000, point=None)
    bet = Horn(stake=20)
    roll = Roll(dice)

    result = bet.settle(state, roll)

    assert result.bankroll_delta == 0
    assert result.remaining_stake == 0


def test_horn_must_be_divisible_by_4():
    """Test that Horn bet must be divisible by 4."""
    state = make_state(bankroll=1000, point=None, prop_min=1)
    bet = Horn(stake=10)  # Not divisible by 4

    with pytest.raises(InsufficientFunds, match="divisible by 4"):
        bet.validate(state)


def test_horn_divisible_by_4_valid():
    """Test that Horn bet divisible by 4 passes validation."""
    state = make_state(bankroll=1000, point=None, prop_min=1)
    bet = Horn(stake=20)

    bet.validate(state)  # Should not raise


# Tests for C&E

def test_c_and_e_wins_on_craps():
    """Test that C&E wins on craps (pays 7:1 on craps portion)."""
    state = make_state(bankroll=1000, point=None)
    bet = CAndE(stake=10)
    roll = Roll((1, 1))  # 2 (craps)

    # $10 bet splits into $5 on craps, $5 on eleven
    # Win $5 on craps (pays 7:1) = $5 + $35 = $40
    result = bet.settle(state, roll)

    assert result.bankroll_delta == 40
    assert result.remaining_stake == 0


def test_c_and_e_wins_on_eleven():
    """Test that C&E wins on eleven (pays 15:1 on eleven portion)."""
    state = make_state(bankroll=1000, point=None)
    bet = CAndE(stake=10)
    roll = Roll((5, 6))  # 11

    # $10 bet splits into $5 on craps, $5 on eleven
    # Win $5 on eleven (pays 15:1) = $5 + $75 = $80
    result = bet.settle(state, roll)

    assert result.bankroll_delta == 80
    assert result.remaining_stake == 0


@pytest.mark.parametrize("dice", [(1, 3), (3, 4), (2, 2)])
def test_c_and_e_loses(dice):
    """Test that C&E loses on non-craps, non-11."""
    state = make_state(bankroll=1000, point=None)
    bet = CAndE(stake=10)
    roll = Roll(dice)

    result = bet.settle(state, roll)

    assert result.bankroll_delta == 0
    assert result.remaining_stake == 0


def test_c_and_e_must_be_divisible_by_2():
    """Test that C&E bet must be divisible by 2."""
    state = make_state(bankroll=1000, point=None, prop_min=1)
    bet = CAndE(stake=11)  # Not divisible by 2

    with pytest.raises(InsufficientFunds, match="divisible by 2"):
        bet.validate(state)


def test_c_and_e_divisible_by_2_valid():
    """Test that C&E bet divisible by 2 passes validation."""
    state = make_state(bankroll=1000, point=None, prop_min=1)
    bet = CAndE(stake=10)

    bet.validate(state)  # Should not raise


# Tests for zero stake

@pytest.mark.parametrize("bet_class", [AnySeven, AnyCraps, AceDeuce, Aces, Boxcars, YoLeven, Horn, CAndE])
def test_prop_zero_stake(bet_class):
    """Test that zero stake returns zero result for all props."""
    state = make_state(bankroll=1000, point=None)
    bet = bet_class(stake=0)
    roll = Roll((3, 4))

    result = bet.settle(state, roll)

    assert result.bankroll_delta == 0
    assert result.remaining_stake == 0


# Standard validation tests

@pytest.mark.parametrize("bet_class,stake", [
    (AnySeven, 5),
    (AnyCraps, 5),
    (AceDeuce, 5),
    (Aces, 5),
    (Boxcars, 5),
    (YoLeven, 5),
    (Horn, 20),  # Divisible by 4
    (CAndE, 10),  # Divisible by 2
])
def test_validate_legal_bet(bet_class, stake):
    """Test that legal prop bets pass validation."""
    state = make_state(bankroll=1000, point=None, prop_min=1)
    bet = bet_class(stake=stake)

    bet.validate(state)


@pytest.mark.parametrize("bet_class", [AnySeven, AnyCraps, AceDeuce, Aces, Boxcars, YoLeven, Horn, CAndE])
def test_validate_negative_bet(bet_class):
    """Test that negative prop bet raises IllegalAction."""
    state = make_state(bankroll=1000, point=None)
    bet = bet_class(stake=-10)

    with pytest.raises(InsufficientFunds, match="cannot be negative"):
        bet.validate(state)


@pytest.mark.parametrize("bet_class,stake", [
    (AnySeven, 100),
    (AnyCraps, 100),
    (AceDeuce, 100),
    (Aces, 100),
    (Boxcars, 100),
    (YoLeven, 100),
    (Horn, 100),
    (CAndE, 100),
])
def test_validate_exceeds_bankroll(bet_class, stake):
    """Test that prop bet exceeding bankroll raises IllegalAction."""
    state = make_state(bankroll=50, point=None)
    bet = bet_class(stake=stake)

    with pytest.raises(InsufficientFunds, match="exceeds bankroll"):
        bet.validate(state)


@pytest.mark.parametrize("bet_class", [AnySeven, AnyCraps, AceDeuce, Aces, Boxcars, YoLeven, Horn, CAndE])
def test_validate_below_prop_min(bet_class):
    """Test that prop bet below prop min raises IllegalAction."""
    state = make_state(bankroll=1000, point=None, prop_min=5)
    bet = bet_class(stake=3)

    with pytest.raises(InsufficientFunds, match="prop minimum"):
        bet.validate(state)


@pytest.mark.parametrize("bet_class,stake", [
    (AnySeven, 1000),
    (AnyCraps, 1000),
    (AceDeuce, 1000),
    (Aces, 1000),
    (Boxcars, 1000),
    (YoLeven, 1000),
    (Horn, 1000),
    (CAndE, 1000),
])
def test_validate_above_table_max(bet_class, stake):
    """Test that prop bet above table max raises IllegalAction."""
    state = make_state(bankroll=10000, point=None, table_max=500)
    bet = bet_class(stake=stake)

    with pytest.raises(InsufficientFunds, match="table maximum"):
        bet.validate(state)


@pytest.mark.parametrize("bet_class", [AnySeven, AnyCraps, AceDeuce, Aces, Boxcars, YoLeven, Horn, CAndE])
def test_validate_zero_stake(bet_class):
    """Test that zero stake passes validation for all props."""
    state = make_state(bankroll=1000, point=None)
    bet = bet_class(stake=0)

    bet.validate(state)  # Should not raise


# Props work during come-out and point

@pytest.mark.parametrize("bet_class,roll", [
    (AnySeven, Roll((3, 4))),  # 7
    (AnyCraps, Roll((1, 1))),  # 2
])
def test_props_work_during_comeout(bet_class, roll):
    """Test that props work during come-out roll."""
    state = make_state(bankroll=1000, point=None)  # Come-out
    bet = bet_class(stake=10)

    result = bet.settle(state, roll)

    assert result.bankroll_delta > 0  # Should win


@pytest.mark.parametrize("bet_class,roll", [
    (AnySeven, Roll((3, 4))),  # 7
    (AnyCraps, Roll((1, 1))),  # 2
])
def test_props_work_during_point(bet_class, roll):
    """Test that props work during point phase."""
    state = make_state(bankroll=1000, point=6)  # Point established
    bet = bet_class(stake=10)

    result = bet.settle(state, roll)

    assert result.bankroll_delta > 0  # Should win
