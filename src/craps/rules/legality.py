from craps.state import TableState
from craps.bets.model import Bets, iter_bets
from craps.bets.registry import BET_REGISTRY
from craps.exceptions import IllegalAction

def validate_target(state: TableState, bets: Bets) -> None:
    """
    Validates that the target bets are legal given the current state.
    Raises IllegalAction if the bets are invalid.
    """
    for slot, stake in iter_bets(bets):
        bet_type = BET_REGISTRY[slot]
        bet_type.validate(state, stake)