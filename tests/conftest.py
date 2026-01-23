from craps.state import TableState
from craps.bets.model import Bets


def make_state(bankroll=1000, point=None, pass_line_bet=0, pass_odds_bet=0, table_min=5, table_max=1000, max_odds=10):
    """Helper to create a TableState."""
    bets_kwargs = {}
    if pass_line_bet != 0:
        bets_kwargs['pass_line'] = pass_line_bet
    if pass_odds_bet != 0:
        bets_kwargs['pass_odds'] = pass_odds_bet

    return TableState(
        bankroll=bankroll,
        roll_count=0,
        point=point,
        bets=Bets(**bets_kwargs),
        last_roll=None,
        is_terminal=False,
        table_min=table_min,
        table_max=table_max,
        max_odds=max_odds,
    )
