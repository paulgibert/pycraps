from dataclasses import replace, fields
from craps.state import TableState
from craps.dice import Roll
from craps.action import Action
from craps.rules.phase import update_phase
from craps.rules.settlement import settle_bets
from craps.rules.legality import validate_action
from craps.bets.model import ActionBets

# Maps ActionBets field names to StateBets field names (only exceptions)
ACTION_TO_STATE_MAPPING = {
    'come_bet': 'come_traveling',
}

def _apply_action(state: TableState, action: Action) -> TableState:
    """
    Applies action to state. Raises IllegalAction if not allowed.
    Merges player-controlled ActionBets into full StateBets.
    """
    validate_action(state, action.bets)

    # Calculate bankroll change and build state bet updates
    new_bankroll = state.bankroll
    state_bet_updates = {}

    for field in fields(ActionBets):
        action_field = field.name
        state_field = ACTION_TO_STATE_MAPPING.get(action_field, action_field)

        action_value = getattr(action.bets, action_field)
        state_value = getattr(state.bets, state_field)

        # Deduct the change from bankroll
        new_bankroll -= (action_value - state_value)

        # Track the update for state bets
        state_bet_updates[state_field] = action_value

    # Merge action bets into state bets (preserving engine-managed come_N bets)
    new_state_bets = replace(state.bets, **state_bet_updates)

    return replace(state, bets=new_state_bets, bankroll=new_bankroll, is_terminal=action.leave)

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
