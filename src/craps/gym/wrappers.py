import gymnasium as gym
from gymnasium import spaces


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