from typing import Optional, Any, Tuple, Dict
from dataclasses import asdict
from copy import deepcopy
import gymnasium as gym
import numpy as np
from craps.bets.model import Bet
from craps.state import TableConfig, TableState
from craps.dice import Roll
from craps.exceptions import IllegalAction, InsufficientFunds
from craps.gym.config import CrapsEnvConfig
from craps.gym.codec import SpaceCodec
from craps.gym.render import (
    snapshot_table_state,
    snapshot_bet_observation,
    snapshot_bet_action
)

class CrapsEnv(gym.Env):
    def __init__(self, env_config: CrapsEnvConfig, table_config: TableConfig, bets: Dict[str, Bet]):
        self._env_config = env_config
        self._table_config = table_config
        self._bets = bets

        self._codec = SpaceCodec(
            table_config=table_config,
            bets=bets,
            init_bankroll=env_config.init_bankroll,
            max_points=env_config.max_points,
            min_bet_inc=env_config.min_bet_inc
        )

        self.action_space = self._codec.action_space
        self.observation_space = self._codec.observation_space

        self.reset()

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None) -> Tuple[Any, Dict]:
        super().reset(seed=seed)
        self._n_steps = 0
        self._n_points = 0
        for bet in self._bets.values():
            bet.reset()
        self._state = TableState(self._table_config, self._bets, self._env_config.init_bankroll)
        return self._codec.encode_observation(self._state, n_points=self._n_points), {}

    def step(self, action: Any) -> Tuple[Any, float, bool, bool, Dict[str, Any]]:
        # Apply bets to table state
        reward = 0.0
        illegal_action = False
        try:
            self._apply_action(action)
        except (IllegalAction, InsufficientFunds):
            reward -= self._env_config.illegal_action_penalty
            illegal_action = True

        # Capture phase before roll for point tracking
        prev_phase = self._state.get_phase()

        # Roll and progress the table state
        roll = self._random_roll()
        self._state.step(roll)

        # Track completed point rounds
        new_phase = self._state.get_phase()
        if prev_phase.point is not None and new_phase.point is None:
            self._n_points += 1

        # Compute outputs
        bankroll = self._state.get_bankroll_size()
        observation = self._codec.encode_observation(self._state, n_points=self._n_points)
        terminated = bankroll <= 0.0 or bankroll >= self._env_config.max_bankroll
        truncated = (not terminated) and self._n_points >= self._env_config.max_points

        self._n_steps += 1

        info = {
            "illegal_action": illegal_action,
            "n_points": self._n_points,
        }
        if terminated or truncated:
            info["terminal_bankroll"] = bankroll
            info["total_steps"] = self._n_steps

        return observation, reward, terminated, truncated, info

    def action_masks(self) -> Dict[str, np.ndarray]:
        return self._codec.build_action_mask(self._state)

    def render(self):
        snap = {
            "table_config": asdict(self._table_config),
            "env_config": asdict(self._env_config),
        }

        snap.update(snapshot_table_state(self._state))

        snap["observation"] = {}
        for name, bet in self._state.bets.items():
            snap["observation"].update(snapshot_bet_observation(name, bet))

        snap["action"] = {}
        for name, bet in self._state.bets.items():
            snap["action"].update(snapshot_bet_action(name, bet))

        return snap

    def _apply_action(self, action: Any):
        for bet_name, bet_type, amount, target in self._codec.decode_action(action):
            if bet_type == 'stake':
                self._state.set_bet_stake(bet_name, amount, target=target)
            else:
                self._state.set_bet_odds(bet_name, amount, target=target)

    def _random_roll(self) -> Roll:
        dice1 = self.np_random.integers(1, 7)
        dice2 = self.np_random.integers(1, 7)
        return Roll((dice1, dice2))