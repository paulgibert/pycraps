from typing import Dict, Any, Optional, Iterator, Tuple
from gymnasium import spaces
from craps.state import TableConfig, TableState
from craps.bets.model import Bet

def build_action_space(config: TableConfig, bets: Dict[str, Bet]) -> spaces.Dict:
    # TODO: When we enforce bet min/max sizing, we will need to dynamically calculate N
    N = len(range(config.table_min, config.table_max, 5)) + 1  # '+ 1' to include bet size = 0

    actions = {
        'leave': spaces.Discrete(2),
    }

    for k, bet in bets.items():
        for tgt in bet.set_stake_targets():
            actions[f'stakes_{k}_{tgt}'] = spaces.Discrete(N)
        for tgt in bet.set_odds_targets():
            actions[f'odds_{k}_{tgt}'] = spaces.Discrete(N)

    return spaces.Dict(actions)

def apply_action(state: TableState, action: Any):
    # Note: updates 'state' in place.
    for bet_key, amount, target in _iter_action_bets(action, state.config):
        state.set_bet_stake(bet_key, amount, target=target)

    for bet_key, amount, target in _iter_action_odds(action, state.config):
        state.set_bet_odds(bet_key, amount, target=target)


def _iter_action_bets(
    action: Any,
    config: TableConfig
) -> Iterator[Tuple[str, float, Optional[int]]]:
    for key, units in action.items():
        if not key.startswith('stakes_'):
            continue

        # key format: stakes_{bet_name}_{target}
        # bet_name may contain underscores, so split from right
        rest, target = key.rsplit('_', 1)
        bet_name = rest[7:]  # remove 'stakes_' prefix

        if target == 'None':
            target = None
        else:
            target = int(target)

        amount = (
            0.0
            if units == 0
            else config.table_min + (units - 1) * 5
        )
        yield bet_name, amount, target


def _iter_action_odds(
    action: Any,
    config: TableConfig
) -> Iterator[Tuple[str, float, Optional[int]]]:
    for key, units in action.items():
        if not key.startswith('odds_'):
            continue

        # key format: odds_{bet_name}_{target}
        # bet_name may contain underscores, so split from right
        rest, target = key.rsplit('_', 1)
        bet_name = rest[5:]  # remove 'odds_' prefix

        if target == 'None':
            target = None
        else:
            target = int(target)

        amount = (
            0.0
            if units == 0
            else config.table_min + (units - 1) * 5
        )
        yield bet_name, amount, target
