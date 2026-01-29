import pytest
from craps.rules.legality import validate_action
from craps.exceptions import InsufficientFunds
from craps.bets.model_old import ActionBets
from conftest import make_state


def set_action_stake(bets: ActionBets, slot: str, stake: int) -> ActionBets:
    """Helper to set stake on ActionBets."""
    from dataclasses import replace
    current_bet = getattr(bets, slot)
    new_bet = replace(current_bet, stake=stake)
    return replace(bets, **{slot: new_bet})


def test_illegal_bet_on_come_out():
    """Test that a bet exceeding bankroll raises IllegalAction on come-out."""
    state = make_state(bankroll=100)
    bets = set_action_stake(ActionBets(), 'pass_line', 200)

    with pytest.raises(InsufficientFunds):
        validate_action(state, bets)


def test_illegal_bet_during_point():
    """Test that changing pass line bet during point raises IllegalAction."""
    state = make_state(bankroll=1000, point=6, pass_line_bet=10)
    bets = set_action_stake(ActionBets(), 'pass_line', 20)

    with pytest.raises(InsufficientFunds):
        validate_action(state, bets)
