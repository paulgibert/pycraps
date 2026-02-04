from typing import Dict, Optional, Any
import numpy as np
from gymnasium import spaces
from craps.state import TableConfig, TableState
from craps.bets.model import Bet
from craps.dice import Roll
from craps.gym.config import CrapsEnvConfig
from craps.constants import POINTS

def build_observation_space(config: TableConfig, bets: Dict[str, Bet]) -> spaces.Dict:
    # TODO: When we enforce bet min/max sizing, we will need to dynamically calculate N
    N = len(range(config.table_min, config.table_max, 5)) + 1  # '+ 1' to include bet size = 0

    obs = {
        'bankroll': spaces.Box(low=-1.0, high=1.0, shape=(1,), dtype=np.float32),
        'point': spaces.Discrete(7),
        'last_roll': spaces.MultiDiscrete([7, 7, 12]),
        'roll_count': spaces.Box(low=-1.0, high=1.0, shape=(1,), dtype=np.float32),
    }

    for k, bet in bets.items():
        for tgt in bet.get_stake_targets():
            obs[f'stakes_{k}_{tgt}'] = spaces.Discrete(N)
        for tgt in bet.get_odds_targets():
            obs[f'odds_{k}_{tgt}'] = spaces.Discrete(N)

    return spaces.Dict(obs)

def encode_observation(state: TableState, table_config: TableConfig, env_config: CrapsEnvConfig) -> Dict[str, Any]:
    obs = {
        'bankroll': _encode_bankroll(state.get_bankroll_size(), env_config.init_bankroll),
        'point': _encode_point(state.get_phase().point),
        'last_roll': _encode_last_roll(state.get_last_roll()),
        'roll_count': _encode_roll_count(state.get_roll_count(), env_config.max_rolls),
    }

    # Flatten bet stakes and odds into top-level keys
    for k, v in _encode_bet_stakes(state.bets, table_config).items():
        obs[f'stakes_{k}'] = v
    for k, v in _encode_bet_odds(state.bets, table_config).items():
        obs[f'odds_{k}'] = v

    return obs

def _encode_bankroll(bankroll: float, init_bankroll: float) -> np.ndarray:
    eps = 1e-6
    x = np.log((bankroll + eps) / init_bankroll)
    return np.array([np.tanh(x)], dtype=np.float32)

def _encode_point(point: Optional[int]) -> np.int64:
    if point is None:
        return np.int64(0)
    if point not in POINTS:
        raise ValueError(f"Provided point is not in {POINTS}.")
    if point <= 6:
        return np.int64(point - 3)
    else:
        return np.int64(point - 4)

def _encode_last_roll(last_roll: Optional[Roll]) -> np.ndarray:
    if last_roll is None:
        return np.array([0, 0, 0], dtype=np.int64)
    return np.array([last_roll[0], last_roll[1], last_roll.total() - 1], dtype=np.int64)

def _encode_roll_count(roll_count: int, max_rolls: int) -> np.ndarray:
    frac_remaining = 1.0 - roll_count / max_rolls
    return np.array([np.tanh(2.0 * frac_remaining - 1.0)], dtype=np.float32)

def _encode_bet_stakes(bets: Dict[str, Bet], config: TableConfig) -> Dict[str, np.int64]:
    stakes = {}
    for k, bet in bets.items():
        for tgt in bet.get_stake_targets():
            amount = bet.get_stake(target=tgt)
            if amount == 0.0:
                units = 0
            else:
                units = int((amount - config.table_min) // 5) + 1  # TODO: Update this when enforcing even returns
            stakes[f'{k}_{tgt}'] = np.int64(units)
    return stakes

def _encode_bet_odds(bets: Dict[str, Bet], config: TableConfig) -> Dict[str, np.int64]:
    odds = {}
    for k, bet in bets.items():
        for tgt in bet.get_odds_targets():
            amount = bet.get_odds(target=tgt)
            if amount == 0.0:
                units = 0
            else:
                units = int((amount - config.table_min) // 5) + 1  # TODO: Update this when enforcing even returns
            odds[f'{k}_{tgt}'] = np.int64(units)
    return odds
