from typing import Optional, Dict, Any, Iterator, Tuple
from math import ceil
import numpy as np
from gymnasium import spaces
from craps.bets.model import Bet
from craps.state import TableConfig, TableState
from craps.dice import Roll
from craps.constants import POINTS


class BetCodec:
    """Encodes/decodes bet amounts to/from discrete indices for gym spaces.

    Maps continuous dollar amounts to discrete indices suitable for gymnasium
    Discrete action/observation spaces. Each bet type has a casino-friendly
    increment that ensures even payouts (no rounding).

    Index mapping:
        0 -> $0 (no bet)
        1 -> minimum bet
        2 -> minimum + increment
        N -> minimum + (N-1) * increment

    The effective increment is the smallest multiple of the bet's natural
    increment that is >= min_increment. This ensures:
        1. Even payouts (always aligned with bet's natural increment)
        2. Manageable action space size (at least min_increment apart)

    Example with min_increment=5:
        - PassLine stake (increment=1): effective=5
        - PlaceBets on 6 (increment=6): effective=6
        - PlaceBets on 5 (increment=5): effective=5
        - Odds on 5 (increment=2): effective=6

    Args:
        config: Table configuration with min/max bet limits.
        bet: The bet instance to encode/decode for.
        min_increment: Minimum spacing between discrete values. The effective
            increment will be the smallest multiple of the bet's natural
            increment that is >= this value. Default is 1 (use bet's natural
            increment).
    """

    def __init__(self, config: TableConfig, bet: Bet, min_increment: int = 1):
        self.config = config
        self.bet = bet
        self.min_increment = min_increment

    def _get_raw_min(self) -> float:
        """Return the raw minimum bet amount based on whether this is a prop bet."""
        return self.config.prop_min if self.bet.is_prop else self.config.table_min

    def _get_stake_min(self, target: Optional[int] = None) -> float:
        """Return the effective stake minimum (aligned to increment)."""
        increment = self._get_stake_increment(target=target)
        return ceil(self._get_raw_min() / increment) * increment

    def _get_odds_min(self, target: Optional[int] = None) -> float:
        """Return the effective odds minimum (aligned to increment)."""
        increment = self._get_odds_increment(target=target)
        return ceil(self._get_raw_min() / increment) * increment

    def _get_stake_increment(self, target: Optional[int] = None) -> int:
        """Return the effective stake increment (>= min_increment, aligned with bet)."""
        bet_increment = self.bet.get_stake_increment(target=target)
        return ceil(self.min_increment / bet_increment) * bet_increment

    def _get_odds_increment(self, target: Optional[int] = None) -> Optional[int]:
        """Return the effective odds increment, or None if bet doesn't support odds."""
        bet_increment = self.bet.get_odds_increment(target=target)
        if bet_increment is None:
            return None
        return ceil(self.min_increment / bet_increment) * bet_increment

    def get_stake_discrete_size(self, target: Optional[int] = None) -> int:
        """Return the number of discrete stake values (for spaces.Discrete)."""
        increment = self._get_stake_increment(target=target)
        return int((self.config.table_max - self._get_stake_min(target=target)) / increment) + 2

    def get_odds_discrete_size(self, target: Optional[int] = None) -> Optional[int]:
        """Return the number of discrete odds values, or None if no odds supported."""
        increment = self._get_odds_increment(target=target)
        if increment is None:
            return None
        return int((self.config.table_max - self._get_odds_min(target=target)) / increment) + 2

    def stake_amount_to_discrete(self, amount: float, target: Optional[int] = None) -> int:
        """Convert a stake dollar amount to its discrete index."""
        if amount == 0:
            return 0
        min_amt = self._get_stake_min(target=target)
        increment = self._get_stake_increment(target=target)
        if amount < min_amt or amount > self.config.table_max:
            raise ValueError(f"Stake amount {amount} out of bounds [{min_amt}, {self.config.table_max}]")
        if (amount - min_amt) % increment != 0:
            raise ValueError(f"Stake amount {amount} not aligned to increment {increment}")
        return int((amount - min_amt) / increment) + 1

    def odds_amount_to_discrete(self, amount: float, target: Optional[int] = None) -> int:
        """Convert an odds dollar amount to its discrete index."""
        if amount == 0:
            return 0
        min_amt = self._get_odds_min(target=target)
        increment = self._get_odds_increment(target=target)
        if amount < min_amt or amount > self.config.table_max:
            raise ValueError(f"Odds amount {amount} out of bounds [{min_amt}, {self.config.table_max}]")
        if (amount - min_amt) % increment != 0:
            raise ValueError(f"Odds amount {amount} not aligned to increment {increment}")
        return int((amount - min_amt) / increment) + 1

    def stake_discrete_to_amount(self, x: int, target: Optional[int] = None) -> float:
        """Convert a discrete index to a stake dollar amount."""
        if x < 0 or x >= self.get_stake_discrete_size(target=target):
            raise ValueError(f"Stake index {x} out of bounds [0, {self.get_stake_discrete_size(target=target) - 1}]")
        if x == 0:
            return 0.0
        increment = self._get_stake_increment(target=target)
        return self._get_stake_min(target=target) + (x - 1) * increment

    def odds_discrete_to_amount(self, x: int, target: Optional[int] = None) -> float:
        """Convert a discrete index to an odds dollar amount."""
        if x < 0 or x >= self.get_odds_discrete_size(target=target):
            raise ValueError(f"Odds index {x} out of bounds [0, {self.get_odds_discrete_size(target=target) - 1}]")
        if x == 0:
            return 0.0
        increment = self._get_odds_increment(target=target)
        return self._get_odds_min(target=target) + (x - 1) * increment


class SpaceCodec:
    """Handles all discrete encoding/decoding for the gym environment.

    Consolidates action space building, observation space building, action
    decoding, and observation encoding into a single class that owns all
    the necessary configuration.

    Args:
        table_config: Table configuration with bet limits.
        bets: Dictionary of bet name to Bet instance.
        init_bankroll: Starting bankroll for observation encoding.
        max_rolls: Maximum rolls for observation encoding.
        min_increment: Minimum spacing between discrete bet values.
    """

    def __init__(
        self,
        table_config: TableConfig,
        bets: Dict[str, Bet],
        init_bankroll: float,
        max_rolls: int,
        min_increment: int = 1
    ):
        self._table_config = table_config
        self._bets = bets
        self._init_bankroll = init_bankroll
        self._max_rolls = max_rolls
        self._min_increment = min_increment

        # Pre-build codecs for each bet
        self._codecs = {
            name: BetCodec(table_config, bet, min_increment)
            for name, bet in bets.items()
        }

        # Build spaces once
        self._action_space = self._build_action_space()
        self._observation_space = self._build_observation_space()

    @property
    def action_space(self) -> spaces.Dict:
        return self._action_space

    @property
    def observation_space(self) -> spaces.Dict:
        return self._observation_space

    def _build_action_space(self) -> spaces.Dict:
        actions = {'leave': spaces.Discrete(2)}

        for name, bet in self._bets.items():
            codec = self._codecs[name]
            for tgt in bet.set_stake_targets():
                actions[f'stake-{name}-{tgt}'] = spaces.Discrete(
                    codec.get_stake_discrete_size(target=tgt)
                )
            for tgt in bet.set_odds_targets():
                actions[f'odds-{name}-{tgt}'] = spaces.Discrete(
                    codec.get_odds_discrete_size(target=tgt)
                )

        return spaces.Dict(actions)

    def _build_observation_space(self) -> spaces.Dict:
        obs = {
            'bankroll': spaces.Box(low=-1.0, high=1.0, shape=(1,), dtype=np.float32),
            'point': spaces.Discrete(7),
            'last_roll': spaces.MultiDiscrete([7, 7, 12]),
            'roll_count': spaces.Box(low=-1.0, high=1.0, shape=(1,), dtype=np.float32),
        }

        for name, bet in self._bets.items():
            codec = self._codecs[name]
            for tgt in bet.get_stake_targets():
                obs[f'stake-{name}-{tgt}'] = spaces.Discrete(
                    codec.get_stake_discrete_size(target=tgt)
                )
            for tgt in bet.get_odds_targets():
                obs[f'odds-{name}-{tgt}'] = spaces.Discrete(
                    codec.get_odds_discrete_size(target=tgt)
                )

        return spaces.Dict(obs)

    def build_action_mask(self, state: TableState) -> Dict[str, np.ndarray]:
        """Build per-key action masks based on game state.

        For each action key, returns a boolean array of length N (matching
        Discrete(N)). Index 0 ($0 / no bet) is always valid. Other indices
        are valid only if the bet is currently accepting wagers.
        """
        masks = {'leave': np.ones(2, dtype=np.int8)}

        for key in self._action_space.spaces:
            if key == 'leave':
                continue

            bet_type, bet_name, target_str = key.split('-')
            target = None if target_str == 'None' else int(target_str)
            bet = state.bets[bet_name]

            if bet_type == 'stake':
                is_on = bet.can_set_stake(target=target)
            else:
                is_on = bet.can_set_odds(target=target)

            size = self._action_space.spaces[key].n
            if is_on:
                mask = np.ones(size, dtype=np.int8)
            else:
                mask = np.zeros(size, dtype=np.int8)
                mask[0] = 1  # index 0 ($0 / no bet) is always valid
            masks[key] = mask

        return masks

    def decode_action(self, action: Dict) -> Iterator[Tuple[str, str, float, Optional[int]]]:
        """Decode a gym action dict into bet operations.

        Yields:
            Tuples of (bet_name, bet_type, amount, target) where bet_type is
            'stake' or 'odds'.
        """
        for key, x in action.items():
            if key == 'leave':
                continue

            parts = key.split('-')
            bet_type, bet_name, target_str = parts[0], parts[1], parts[2]
            target = None if target_str == 'None' else int(target_str)

            if bet_type == 'stake':
                amount = self._codecs[bet_name].stake_discrete_to_amount(x, target=target)
                yield bet_name, 'stake', amount, target
            elif bet_type == 'odds':
                amount = self._codecs[bet_name].odds_discrete_to_amount(x, target=target)
                yield bet_name, 'odds', amount, target

    def encode_observation(self, state: TableState) -> Dict[str, Any]:
        """Encode the table state into a gym observation dict."""
        obs = {
            'bankroll': self._encode_bankroll(state.get_bankroll_size()),
            'point': self._encode_point(state.get_phase().point),
            'last_roll': self._encode_last_roll(state.get_last_roll()),
            'roll_count': self._encode_roll_count(state.get_roll_count()),
        }

        # Encode bet stakes and odds
        for name, bet in self._bets.items():
            codec = self._codecs[name]
            for tgt in bet.get_stake_targets():
                amount = bet.get_stake(target=tgt)
                obs[f'stake-{name}-{tgt}'] = np.int64(
                    codec.stake_amount_to_discrete(amount, target=tgt)
                )
            for tgt in bet.get_odds_targets():
                amount = bet.get_odds(target=tgt)
                obs[f'odds-{name}-{tgt}'] = np.int64(
                    codec.odds_amount_to_discrete(amount, target=tgt)
                )

        return obs

    def _encode_bankroll(self, bankroll: float) -> np.ndarray:
        eps = 1e-6
        x = np.log((bankroll + eps) / self._init_bankroll)
        return np.array([np.tanh(x)], dtype=np.float32)

    def _encode_point(self, point: Optional[int]) -> np.int64:
        if point is None:
            return np.int64(0)
        if point not in POINTS:
            raise ValueError(f"Provided point is not in {POINTS}.")
        if point <= 6:
            return np.int64(point - 3)
        else:
            return np.int64(point - 4)

    def _encode_last_roll(self, last_roll: Optional[Roll]) -> np.ndarray:
        if last_roll is None:
            return np.array([0, 0, 0], dtype=np.int64)
        return np.array([last_roll[0], last_roll[1], last_roll.total() - 1], dtype=np.int64)

    def _encode_roll_count(self, roll_count: int) -> np.ndarray:
        frac_remaining = 1.0 - roll_count / self._max_rolls
        return np.array([np.tanh(2.0 * frac_remaining - 1.0)], dtype=np.float32)
