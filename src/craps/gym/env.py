from typing import Optional, Any, Tuple, Dict
import gymnasium as gym
import numpy as np
from craps.bets.model import Bet
from craps.state import TableConfig, TableState
from craps.phase import TablePhase
from craps.dice import Roll
from craps.exceptions import IllegalAction, InsufficientFunds
from craps.gym.action import build_action_space, apply_action
from craps.gym.observation import build_observation_space, encode_observation
from craps.gym.config import CrapsEnvConfig

class CrapsEnv(gym.Env):
    def __init__(self, env_config: CrapsEnvConfig, table_config: TableConfig, bets: Dict[str, Bet]):
        self.env_config = env_config
        self.table_config = table_config
        self.bets = bets

        self.action_space = build_action_space(table_config, bets)
        self.observation_space = build_observation_space(table_config, bets)

        self.reset()

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None) -> Tuple[Any, Dict]:
        super().reset(seed=seed)
        self._n_steps = 0
        self._prev_bankroll = self.env_config.init_bankroll
        self._state = TableState(self.table_config, self.bets, self.env_config.init_bankroll)
        observation = encode_observation(self._state, self.table_config, self.env_config)
        return observation, {}
    
    def step(self, action: Any) -> Tuple[Any, float, bool, bool, Dict[str, Any]]:
        # Apply bets to table state
        try:
            apply_action(self._state, action)
        except (IllegalAction, InsufficientFunds):
            # TODO: Consider different feedback based on the error type
            observation = encode_observation(self._state, self.table_config, self.env_config)
            return observation, -1.0, True, False, {}

        # Roll and progress the table state
        roll = self._random_roll()
        self._state.step(roll)

        # Encode observation
        observation = encode_observation(self._state, self.table_config, self.env_config)

        # Compute reward
        reward = self._reward()

        # Determine termination
        terminated = (
            self._state.get_bankroll_size() <= 0.0
            or action['leave'] == 1
        )

        # Determine truncation
        truncated = self._n_steps >= self.env_config.max_steps

        info = {}

        self._n_steps += 1
        self._prev_bankroll = self._state.get_bankroll_size()

        return observation, reward, terminated, truncated, info

    def render(self):
        # TODO
        pass

    def _reward(self) -> float:
        # TODO: This is just a placeholder
        eps = 1e-6
        return float(np.log((self._state.get_bankroll_size() + eps) / (self._prev_bankroll + eps)))

    def _random_roll(self) -> Roll:
        dice1 = self.np_random.integers(1, 7)
        dice2 = self.np_random.integers(1, 7)
        return Roll((dice1, dice2))
