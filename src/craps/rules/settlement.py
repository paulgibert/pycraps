from dataclasses import replace
from craps.state import TableState
from craps.dice import Roll
from craps.bets.model import iter_bets, set_stake


def settle_bets(state: TableState, roll: Roll) -> TableState:
    """
    Settles table bets based on the roll and updates bankroll.
    Does not update the table phase (point value, roll count, etc).
    """
    bankroll = state.bankroll
    new_bets = state.bets

    for slot, bet in iter_bets(state.bets):
        if bet.stake == 0:
            continue

        result = bet.settle(state, roll)

        bankroll += result.bankroll_delta
        new_bets = set_stake(new_bets, slot, result.remaining_stake)

    return replace(
        state,
        bankroll=bankroll,
        bets=new_bets,
    )
