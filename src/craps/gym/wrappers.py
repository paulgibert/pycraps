from collections import deque
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from craps.gym.reward import cpt_utility

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
        bankroll_ref: float,
        maxsize: int=256,
        minsize: int=64,
        outcome_bins: int=10
    ):
        self._minsize = minsize
        self.buffer = deque(maxlen=maxsize)
        self._bankroll_ref = bankroll_ref
        self._outcome_bins = outcome_bins

    def add(self, terminal_bankroll):
        self.buffer.append(terminal_bankroll)

    def utility(self):
        if len(self.buffer) < self._minsize:
            return 0.0
        return cpt_utility(
            np.array(self.buffer),
            ref=self._bankroll_ref,
            n_bins=self._outcome_bins
        )

class CPTRewardWrapper(gym.Wrapper):
    def __init__(self, env, buffer):
        super().__init__(env)
        self.buffer = buffer
        self.prev_cpt = 0.0

    def reset(self, **kwargs):
        self.prev_cpt = self.buffer.utility()
        return self.env.reset(**kwargs)

    def step(self, action):
        obs, reward, done, trunc, info = self.env.step(action)

        if done:
            bankroll = info["terminal_bankroll"]
            self.buffer.add(bankroll)
            new_cpt = self.buffer.utility()
            reward += new_cpt - self.prev_cpt

        return obs, reward, done, trunc, info
