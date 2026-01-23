from dataclasses import replace
from craps.state import TableState
from craps.dice import Roll
from craps.action import Action
from craps.rules.phase import update_phase
from craps.rules.settlement import settle_bets
from craps.rules.legality import validate_action
from craps.bets.model import StateBets

def _apply_action(state: TableState, action: Action) -> TableState:
    """
    Applies action to state. Raises IllegalAction if not allowed.
    Merges player-controlled ActionBets into full StateBets.
    """
    validate_action(state, action.bets)

    # Calculate bankroll change and build new state bets
    new_bankroll = state.bankroll

    # Update player-controlled bets
    new_bankroll -= (action.bets.pass_line - state.bets.pass_line)
    new_bankroll -= (action.bets.pass_odds - state.bets.pass_odds)
    new_bankroll -= (action.bets.come_bet - state.bets.come_traveling)

    # Merge action bets into state bets (preserving engine-managed bets)
    new_state_bets = replace(
        state.bets,
        pass_line=action.bets.pass_line,
        pass_odds=action.bets.pass_odds,
        come_traveling=action.bets.come_bet,
        # come_4, come_5, etc. are preserved from state (engine-managed)
    )

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
