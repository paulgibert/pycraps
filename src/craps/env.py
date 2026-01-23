from dataclasses import replace
from craps.state import TableState
from craps.dice import Roll
from craps.action import Action
from craps.rules.phase import update_phase
from craps.rules.settlement import settle_bets
from craps.rules.legality import validate_target
from craps.bets.model import iter_bets

def _apply_action(state: TableState, action: Action) -> TableState:
    """
    Applies action to state. Raises IllegalAction if not allowed.
    """
    validate_target(state, action.bets)

    # Calculate bankroll change from bet adjustments
    new_bankroll = state.bankroll
    for slot, new_stake in iter_bets(action.bets):
        current_stake = getattr(state.bets, slot)
        new_bankroll -= (new_stake - current_stake)

    return replace(state, bets=action.bets, bankroll=new_bankroll, is_terminal=action.leave)

def step(state: TableState, action: Action, roll: Roll) -> TableState:
    """
    Applies an action, resolves a single roll, and returns the next table state.
    """
    after_action = _apply_action(state, action)
    after_settlement = settle_bets(after_action, roll)
    next_state = update_phase(after_settlement, roll)
    return replace(
        next_state,
        last_roll=roll,
        roll_count=state.roll_count + 1
    )
