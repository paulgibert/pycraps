from craps.state import TableState
from craps.bets.model import Bets


def make_state(bankroll=1000, point=None, pass_line_bet=0, table_min=5, table_max=1000):
    """Helper to create a TableState."""
    return TableState(
        bankroll=bankroll,
        roll_count=0,
        point=point,
        bets=Bets(pass_line=pass_line_bet),
        last_roll=None,
        is_terminal=False,
        table_min=table_min,
        table_max=table_max,
    )
