from dataclasses import fields
from craps.state import TableState
from craps.bets.model import ActionBets, StateBets, iter_bets
from craps.bets.registry import BET_REGISTRY
from craps.exceptions import IllegalAction

def validate_action(state: TableState, action_bets: ActionBets) -> None:
    """
    Validates that the action bets are legal given the current state.
    Raises IllegalAction if the bets are invalid.

    Args:
        state: Current table state
        action_bets: Player-controlled bets (pass_line, pass_odds, come_bet)
    """
    for field in fields(ActionBets):
        stake = getattr(action_bets, field.name)
        bet_type = BET_REGISTRY[field.name]
        bet_type.validate(state, stake)

def validate_target(state: TableState, bets: StateBets) -> None:
    """
    Validates that the target bets are legal given the current state.
    Raises IllegalAction if the bets are invalid.

    This function validates all bets in StateBets, including engine-managed ones.
    For validating player actions, use validate_action() instead.
    """
    for slot, stake in iter_bets(bets):
        bet_type = BET_REGISTRY[slot]
        bet_type.validate(state, stake)