from craps.state import TableState
from craps.bets.model import StateBets, set_stake


def make_state(
    bankroll=1000,
    point=None,
    pass_line_bet=0,
    pass_odds_bet=0,
    come_traveling_bet=0,
    come_4=0,
    come_5=0,
    come_6=0,
    come_8=0,
    come_9=0,
    come_10=0,
    come_odds_4=0,
    come_odds_5=0,
    come_odds_6=0,
    come_odds_8=0,
    come_odds_9=0,
    come_odds_10=0,
    table_min=5,
    table_max=1000,
    max_odds=10,
    prop_min=1
):
    """Helper to create a TableState."""
    bets = StateBets()

    # Build bets using set_stake for non-zero values
    if pass_line_bet != 0:
        bets = set_stake(bets, 'pass_line', pass_line_bet)
    if pass_odds_bet != 0:
        bets = set_stake(bets, 'pass_odds', pass_odds_bet)
    if come_traveling_bet != 0:
        bets = set_stake(bets, 'come_traveling', come_traveling_bet)
    if come_4 != 0:
        bets = set_stake(bets, 'come_4', come_4)
    if come_5 != 0:
        bets = set_stake(bets, 'come_5', come_5)
    if come_6 != 0:
        bets = set_stake(bets, 'come_6', come_6)
    if come_8 != 0:
        bets = set_stake(bets, 'come_8', come_8)
    if come_9 != 0:
        bets = set_stake(bets, 'come_9', come_9)
    if come_10 != 0:
        bets = set_stake(bets, 'come_10', come_10)
    if come_odds_4 != 0:
        bets = set_stake(bets, 'come_odds_4', come_odds_4)
    if come_odds_5 != 0:
        bets = set_stake(bets, 'come_odds_5', come_odds_5)
    if come_odds_6 != 0:
        bets = set_stake(bets, 'come_odds_6', come_odds_6)
    if come_odds_8 != 0:
        bets = set_stake(bets, 'come_odds_8', come_odds_8)
    if come_odds_9 != 0:
        bets = set_stake(bets, 'come_odds_9', come_odds_9)
    if come_odds_10 != 0:
        bets = set_stake(bets, 'come_odds_10', come_odds_10)

    return TableState(
        bankroll=bankroll,
        roll_count=0,
        point=point,
        bets=bets,
        last_roll=None,
        is_terminal=False,
        table_min=table_min,
        table_max=table_max,
        max_odds=max_odds,
        prop_min=prop_min,
    )
