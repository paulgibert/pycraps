from typing import Optional, Any, Tuple, Dict
import gymnasium as gym
import numpy as np
from craps.bets.model import Bet
from craps.state import TableConfig, TableState
from craps.dice import Roll
from craps.exceptions import IllegalAction, InsufficientFunds
from craps.gym.config import CrapsEnvConfig
from craps.gym.codec import SpaceCodec


class CrapsEnv(gym.Env):
    def __init__(self, env_config: CrapsEnvConfig, table_config: TableConfig, bets: Dict[str, Bet]):
        self._env_config = env_config
        self._table_config = table_config
        self._bets = bets

        self._codec = SpaceCodec(
            table_config=table_config,
            bets=bets,
            init_bankroll=env_config.init_bankroll,
            max_rolls=env_config.max_rolls,
            min_increment=env_config.min_increment
        )

        self.action_space = self._codec.action_space
        self.observation_space = self._codec.observation_space

        self.reset()

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None) -> Tuple[Any, Dict]:
        super().reset(seed=seed)
        self._n_steps = 0
        self._prev_bankroll = self._env_config.init_bankroll
        self._state = TableState(self._table_config, self._bets, self._env_config.init_bankroll)
        return self._codec.encode_observation(self._state), {}

    def step(self, action: Any) -> Tuple[Any, float, bool, bool, Dict[str, Any]]:
        # Apply bets to table state
        try:
            self._apply_action(action)
        except (IllegalAction, InsufficientFunds):
            # TODO: Consider different feedback based on the error type
            return self._codec.encode_observation(self._state), -1.0, True, False, {}

        # Roll and progress the table state
        roll = self._random_roll()
        self._state.step(roll)

        # Compute outputs
        observation = self._codec.encode_observation(self._state)
        reward = self._compute_reward()
        terminated = self._state.get_bankroll_size() <= 0.0 or action['leave'] == 1
        truncated = self._n_steps >= self._env_config.max_steps

        self._n_steps += 1
        self._prev_bankroll = self._state.get_bankroll_size()

        return observation, reward, terminated, truncated, {}

    def render(self):
        pass

    def _apply_action(self, action: Any):
        for bet_name, bet_type, amount, target in self._codec.decode_action(action):
            if bet_type == 'stake':
                self._state.set_bet_stake(bet_name, amount, target=target)
            else:
                self._state.set_bet_odds(bet_name, amount, target=target)

    def _compute_reward(self) -> float:
        # TODO: This is just a placeholder
        eps = 1e-6
        return float(np.log((self._state.get_bankroll_size() + eps) / (self._prev_bankroll + eps)))

    def _random_roll(self) -> Roll:
        dice1 = self.np_random.integers(1, 7)
        dice2 = self.np_random.integers(1, 7)
        return Roll((dice1, dice2))