"""
table_config: ...
env_config: ...
bankroll: ...
point: ...
last_roll: ...
roll_count: ...
curr_observation:
    key: value
last_action:
    key: value
"""
from typing import Dict
from craps.bets.model import Bet
from craps.state import TableState

def snapshot_table_state(state: TableState) -> Dict:
    return {
        "point": state.get_phase().point,
        "bankroll": state.get_bankroll_size(),
        "last_roll": str(state.get_last_roll()),
        "roll_count": state.get_roll_count()
    }

def snapshot_bet_action(name: str, bet: Bet) -> Dict:
    snap = {}
    # Stakes
    for tgt in bet.set_stake_targets():
        snap[f"stake.{name}.{tgt}"] = bet.get_stake(target=tgt)
    # Odds
    for tgt in bet.set_odds_targets():
        snap[f"odds.{name}.{tgt}"] = bet.get_odds(target=tgt)
    return snap

def snapshot_bet_observation(name: str, bet: Bet) -> Dict:
    snap = {}
    # Stakes
    for tgt in bet.get_stake_targets():
        snap[f"stake.{name}.{tgt}"] = bet.get_stake(target=tgt)
    # Odds
    for tgt in bet.get_odds_targets():
        snap[f"odds.{name}.{tgt}"] = bet.get_odds(target=tgt)
    return snap