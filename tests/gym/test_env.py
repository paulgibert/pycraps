import numpy as np
import pytest

from craps.gym.env import CrapsEnv, ILLEGAL_ACTION_REWARD


@pytest.fixture
def env():
    e = CrapsEnv(
        init_bankroll=1000,
        table_min=25,
        table_max=1000,
        max_odds=5,
        prop_min=5,
    )
    return e


class TestReset:
    def test_returns_obs_and_info(self, env):
        obs, info = env.reset(seed=42)
        assert isinstance(obs, dict)
        assert isinstance(info, dict)

    def test_obs_keys(self, env):
        obs, _ = env.reset(seed=42)
        assert set(obs.keys()) == {'bankroll', 'point', 'last_roll', 'roll_count', 'bets'}

    def test_initial_point_is_off(self, env):
        obs, _ = env.reset(seed=42)
        assert obs['point'] == 0  # None -> 0

    def test_deterministic_with_seed(self, env):
        obs1, _ = env.reset(seed=123)
        obs2, _ = env.reset(seed=123)
        assert obs1['bankroll'] == obs2['bankroll']
        np.testing.assert_array_equal(obs1['bets'], obs2['bets'])


class TestStep:
    def test_returns_five_tuple(self, env):
        env.reset(seed=42)
        action = np.zeros(env.action_space.shape, dtype=np.int64)
        result = env.step(action)
        assert len(result) == 5

    def test_no_bet_action(self, env):
        env.reset(seed=42)
        action = np.zeros(env.action_space.shape, dtype=np.int64)
        obs, reward, terminated, truncated, info = env.step(action)
        assert isinstance(obs, dict)
        assert not truncated

    def test_illegal_action_freezes_state(self, env):
        obs_before, _ = env.reset(seed=42)
        # Try to place pass odds without a point — should be illegal
        action = np.zeros(env.action_space.shape, dtype=np.int64)
        action[2] = 1  # pass_odds at index 1 in bets, index 2 in full action (after leave flag)
        obs_after, reward, _, _, _ = env.step(action)
        assert reward == ILLEGAL_ACTION_REWARD
        assert obs_before['point'] == obs_after['point']
        assert obs_before['bankroll'] == obs_after['bankroll']
        np.testing.assert_array_equal(obs_before['bets'], obs_after['bets'])

    def test_seeded_rolls_are_deterministic(self, env):
        env.reset(seed=42)
        action = np.zeros(env.action_space.shape, dtype=np.int64)
        obs1, _, _, _, _ = env.step(action)

        env.reset(seed=42)
        obs2, _, _, _, _ = env.step(action)

        np.testing.assert_array_equal(obs1['last_roll'], obs2['last_roll'])