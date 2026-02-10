from collections import deque
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from craps.gym.reward import cpt_utility_from_returns

class FlattenActionWrapper(gym.ActionWrapper):
    """Flatten a Dict action space of Discrete spaces into a MultiDiscrete space."""

    def __init__(self, env):
        super().__init__(env)

        # Build MultiDiscrete from Dict of Discrete spaces
        self._action_keys = list(env.action_space.spaces.keys())
        nvec = [env.action_space.spaces[k].n for k in self._action_keys]
        self.action_space = spaces.MultiDiscrete(nvec)

    def action(self, action):
        # Convert MultiDiscrete array back to Dict
        return {k: int(action[i]) for i, k in enumerate(self._action_keys)}

    def action_masks(self) -> np.ndarray:
        masks = self.env.action_masks()
        return np.concatenate([masks[k] for k in self._action_keys])

class CPTBuffer:
    def __init__(
        self,
        maxsize: int=256,
        minsize: int=64,
        outcome_bins: int=10
    ):
        self._minsize = minsize
        self.buffer = deque(maxlen=maxsize)
        self._outcome_bins = outcome_bins

    def add(self, fractional_return: float):
        self.buffer.append(fractional_return)

    def utility(self):
        if len(self.buffer) < self._minsize:
            return 0.0
        return cpt_utility_from_returns(
            np.array(self.buffer),
            n_bins=self._outcome_bins
        )

    def is_full(self) -> bool:
        return len(self.buffer) >= self._minsize

class CPTRewardWrapper(gym.Wrapper):
    def __init__(self, env, buffer, init_bankroll: float, entertainment_cost: float = 0.0):
        super().__init__(env)
        self.buffer = buffer
        self.prev_cpt = 0.0
        self._init_bankroll = init_bankroll
        self._entertainment_cost = entertainment_cost
        self._reset_episode_stats()

    def _reset_episode_stats(self):
        self._ep_reward_total = 0.0
        self._ep_illegal_actions = 0

    def reset(self, **kwargs):
        self.prev_cpt = self.buffer.utility()
        self._reset_episode_stats()
        return self.env.reset(**kwargs)

    def step(self, action):
        obs, reward, done, trunc, info = self.env.step(action)

        self._ep_illegal_actions += int(info["illegal_action"])
        self._ep_reward_total += reward

        cpt_delta = 0.0
        if done or trunc:
            n_points = info["n_points"]
            adjusted_ref = max(
                1e-6,
                self._init_bankroll - n_points * self._entertainment_cost
            )

            terminal_bankroll = info["terminal_bankroll"]
            fractional_return = (terminal_bankroll - adjusted_ref) / adjusted_ref

            self.buffer.add(fractional_return)

            if self.buffer.is_full():
                new_cpt = self.buffer.utility()
                cpt_delta = new_cpt - self.prev_cpt
                reward += cpt_delta

            self._ep_reward_total += cpt_delta

            info["ep_reward_total"] = self._ep_reward_total
            info["ep_cpt_delta"] = cpt_delta
            info["ep_cpt_utility"] = self.buffer.utility()
            info["ep_illegal_actions"] = self._ep_illegal_actions
            info["adjusted_ref"] = adjusted_ref
            info["fractional_return"] = fractional_return

        return obs, reward, done, trunc, info
