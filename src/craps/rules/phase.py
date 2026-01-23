from dataclasses import replace
from craps.state import TableState
from craps.dice import Roll

def update_phase(state: TableState, roll: Roll) -> TableState:
    """
    Updates the table phase based on the roll (point value).
    Does not pay out bets or update bankroll, roll_count, or last_roll.
    """
    if state.point is None:
        if roll.total() not in (2, 3, 7, 11, 12):
            return replace(state, point=roll.total())
        else:
            return state
    elif roll.total() == state.point:
        return replace(state, point=None)
    elif roll.total() == 7:
        return replace(state, point=None)
    else:
        return state
