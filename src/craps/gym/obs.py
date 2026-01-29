from typing import Optional

import numpy as np
from gymnasium import spaces

from craps.state import TableState
from craps.dice import Roll
from craps.gym.codec import BetCodec

POINT_ENCODING = {None: 0, 4: 1, 5: 2, 6: 3, 8: 4, 9: 5, 10: 6}


def make_observation_space(bet_codec: BetCodec, max_bankroll: int, max_roll_count: int) -> spaces.Dict:
    return spaces.Dict({
        'bankroll': spaces.Box(low=0.0, high=1.0, shape=()),
        'point': spaces.Discrete(7),
        'last_roll': spaces.MultiDiscrete([7, 7, 12]),
        'roll_count': spaces.Box(low=0.0, high=1.0, shape=()),
        'bets': spaces.MultiDiscrete(bet_codec.n_values()),
    })


def encode_observation(
    state: TableState,
    bet_codec: BetCodec,
    max_bankroll: int,
    max_roll_count: int,
) -> dict:
    return {
        'bankroll': _encode_bankroll(state.bankroll, max_bankroll),
        'point': POINT_ENCODING[state.point],
        'last_roll': _encode_last_roll(state.last_roll),
        'roll_count': _encode_roll_count(state.roll_count, max_roll_count),
        'bets': bet_codec.encode(state.bets),
    }


def _encode_bankroll(bankroll: int, max_bankroll: int) -> float:
    return np.log(1 + bankroll) / np.log(1 + max_bankroll)


def _encode_last_roll(last_roll: Optional[Roll]) -> np.ndarray:
    # All zeros means "no roll yet"
    if last_roll is None:
        return np.array([0, 0, 0])
    return np.array([
        last_roll[0],           # 1-6
        last_roll[1],           # 1-6
        last_roll.total() - 1,  # 1-11
    ])


def _encode_roll_count(count: int, max_roll_count: int) -> float:
    return min(count / max_roll_count, 1.0)
