import pytest
from craps.rules.legality import validate_action
from craps.exceptions import IllegalAction
from craps.bets.model import ActionBets
from conftest import make_state


def test_illegal_bet_on_come_out():
    """Test that a bet exceeding bankroll raises IllegalAction on come-out."""
    state = make_state(bankroll=100)
    bets = ActionBets(pass_line=200)

    with pytest.raises(IllegalAction):
        validate_action(state, bets)


def test_illegal_bet_during_point():
    """Test that changing pass line bet during point raises IllegalAction."""
    state = make_state(bankroll=1000, point=6, pass_line_bet=10)
    bets = ActionBets(pass_line=20)

    with pytest.raises(IllegalAction):
        validate_action(state, bets)
