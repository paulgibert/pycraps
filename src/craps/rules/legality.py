from craps.state import TableState
from craps.bets.model import ActionBets, iter_bets


def validate_action(state: TableState, action_bets: ActionBets) -> None:
    """
    Validates that the action bets are legal given the current state.
    Raises IllegalAction if the bets are invalid.

    Args:
        state: Current table state
        action_bets: Player-controlled bets
    """
    for _, bet in iter_bets(action_bets):
        bet.validate(state)
