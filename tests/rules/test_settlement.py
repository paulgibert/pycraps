from craps.rules.settlement import settle_bets
from craps.dice import Roll
from conftest import make_state


def test_winning_bet():
    """Test that winning pass line bet increases bankroll."""
    state = make_state(bankroll=1000, pass_line_bet=10)
    roll = Roll((3, 4))  # 7 on come-out

    next_state = settle_bets(state, roll)

    assert next_state.bankroll == 1020  # Won 20
    assert next_state.bets.pass_line.stake == 0  # Bet resolved


def test_losing_bet():
    """Test that losing pass line bet decreases bankroll."""
    state = make_state(bankroll=1000, pass_line_bet=10)
    roll = Roll((1, 1))  # 2 on come-out

    next_state = settle_bets(state, roll)

    assert next_state.bankroll == 1000  # Lost stake (already deducted)
    assert next_state.bets.pass_line.stake == 0  # Bet resolved


def test_point_established():
    """Test that point establishment keeps bet on table."""
    state = make_state(bankroll=1000, pass_line_bet=10)
    roll = Roll((3, 3))  # 6

    next_state = settle_bets(state, roll)

    assert next_state.bankroll == 1000  # No change
    assert next_state.bets.pass_line.stake == 10  # Bet remains


def test_zero_stake():
    """Test that zero stake bets are handled correctly."""
    state = make_state(bankroll=1000, pass_line_bet=0)
    roll = Roll((3, 4))  # 7

    next_state = settle_bets(state, roll)

    assert next_state.bankroll == 1000
    assert next_state.bets.pass_line.stake == 0
