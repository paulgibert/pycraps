from typing import Optional

import gymnasium as gym
from gymnasium import spaces
from craps.state import TableState
from craps.action import Action
from craps.bets.model_old import ActionBets, StateBets, iter_bets
from craps.env import step
from craps.dice import Roll
from craps.exceptions import InsufficientFunds
from craps.gym.codec import BetCodec
from craps.gym.obs import make_observation_space, encode_observation

ILLEGAL_ACTION_REWARD = -1

POINT_DISPLAY = {None: 'OFF', 4: '4', 5: '5', 6: '6', 8: '8', 9: '9', 10: '10'}


class CrapsEnv(gym.Env):
    metadata = {'render_modes': ['human', 'ansi']}

    def __init__(
            self,
            init_bankroll: int = 1000,
            max_bankroll: int = 10000,
            max_roll_count: int = 800,
            table_min: int = 25,
            table_max: int = 1000,
            max_odds: int = 5,
            prop_min: int = 5,
            render_mode: Optional[str] = None,
        ):
        self.init_bankroll = init_bankroll
        self.max_bankroll = max_bankroll
        self.max_roll_count = max_roll_count
        self.table_min = table_min
        self.table_max = table_max
        self.max_odds = max_odds
        self.prop_min = prop_min
        self.render_mode = render_mode

        self._action_codec = BetCodec(ActionBets, table_min, table_max, prop_min)
        self._obs_codec = BetCodec(StateBets, table_min, table_max, prop_min)

        self.action_space = spaces.MultiDiscrete(
            [2] + self._action_codec.n_values()
        )
        self.observation_space = make_observation_space(
            self._obs_codec, max_bankroll, max_roll_count
        )

        self._table_state = None
        self._last_action_bets = None
        self._last_roll = None
        self._last_illegal = False

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None):
        super().reset(seed=seed)

        self._table_state = TableState(
            bankroll=self.init_bankroll,
            roll_count=0,
            point=None,
            bets=StateBets(),
            last_roll=None,
            is_terminal=False,
            table_min=self.table_min,
            table_max=self.table_max,
            max_odds=self.max_odds,
            prop_min=self.prop_min,
        )
        self._last_action_bets = None
        self._last_roll = None
        self._last_illegal = False

        obs = encode_observation(
            self._table_state, self._obs_codec,
            self.max_bankroll, self.max_roll_count,
        )
        return obs, {}

    def step(self, x):
        bets = self._action_codec.decode(x[1:])
        action = Action(bets=bets, leave=(x[0] == 1))
        roll = Roll(tuple(self.np_random.integers(1, 7, size=2)))

        self._last_action_bets = bets
        self._last_roll = roll

        prev_state = self._table_state
        try:
            self._table_state = step(self._table_state, action, roll)
            reward = 0  # TODO: bankroll delta
            self._last_illegal = False
        except InsufficientFunds:
            self._table_state = prev_state
            reward = ILLEGAL_ACTION_REWARD
            self._last_illegal = True

        obs = encode_observation(
            self._table_state, self._obs_codec,
            self.max_bankroll, self.max_roll_count,
        )
        terminated = self._table_state.is_terminal
        truncated = False
        info = {}

        return obs, reward, terminated, truncated, info

    def render(self):
        s = self._table_state
        lines = []

        # Roll and state header
        roll_str = f'({self._last_roll[0]}, {self._last_roll[1]}) = {self._last_roll.total()}' if self._last_roll else 'None'
        lines.append(
            f'Roll #{s.roll_count}: {roll_str}    '
            f'Point: {POINT_DISPLAY[s.point]}    '
            f'Bankroll: ${s.bankroll}'
        )

        # Action taken
        if self._last_action_bets is not None:
            action_parts = [
                f'{name}=${bet.stake}'
                for name, bet in iter_bets(self._last_action_bets)
                if bet.stake > 0
            ]
            action_str = ', '.join(action_parts) if action_parts else 'no bets'
            lines.append(f'Action: {action_str}')

        # Illegal action indicator
        if self._last_illegal:
            lines.append('Result: ILLEGAL (state frozen)')

        # Active bets on the table
        active = [
            f'{name}=${bet.stake}'
            for name, bet in iter_bets(s.bets)
            if bet.stake > 0
        ]
        if active:
            lines.append(f'Active bets: {", ".join(active)}')

        output = '\n'.join(lines)

        if self.render_mode == 'human':
            print(output)
        return output