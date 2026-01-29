import numpy as np
import pytest

from craps.bets.model import ActionBets, StateBets, set_stake, iter_bets
from craps.gym.codec import BetCodec


TABLE_MIN = 25
TABLE_MAX = 1000
PROP_MIN = 5


@pytest.fixture
def action_codec():
    return BetCodec(ActionBets, TABLE_MIN, TABLE_MAX, PROP_MIN)


@pytest.fixture
def state_codec():
    return BetCodec(StateBets, TABLE_MIN, TABLE_MAX, PROP_MIN)


class TestRoundTrip:
    def test_all_zeros(self, action_codec):
        bets = ActionBets()
        encoded = action_codec.encode(bets)
        decoded = action_codec.decode(encoded)
        for (_, orig), (_, rt) in zip(iter_bets(bets), iter_bets(decoded)):
            assert orig.stake == rt.stake

    def test_single_bet_at_min(self, action_codec):
        bets = set_stake(ActionBets(), 'pass_line', TABLE_MIN)
        encoded = action_codec.encode(bets)
        decoded = action_codec.decode(encoded)
        assert decoded.pass_line.stake == TABLE_MIN

    def test_prop_bet_at_min(self, action_codec):
        bets = set_stake(ActionBets(), 'any_seven', PROP_MIN)
        encoded = action_codec.encode(bets)
        decoded = action_codec.decode(encoded)
        assert decoded.any_seven.stake == PROP_MIN

    def test_multiple_bets(self, action_codec):
        bets = ActionBets()
        bets = set_stake(bets, 'pass_line', 50)
        bets = set_stake(bets, 'place_6', 30)  # min for place_6 is ceil(25/6)*6 = 30
        encoded = action_codec.encode(bets)
        decoded = action_codec.decode(encoded)
        assert decoded.pass_line.stake == 50
        assert decoded.place_6.stake == 30


class TestEncode:
    def test_zero_stake_encodes_to_zero(self, action_codec):
        bets = ActionBets()
        encoded = action_codec.encode(bets)
        assert (encoded == 0).all()

    def test_min_stake_encodes_to_one(self, action_codec):
        bets = set_stake(ActionBets(), 'pass_line', TABLE_MIN)
        encoded = action_codec.encode(bets)
        # pass_line is the first slot
        assert encoded[0] == 1


class TestDecode:
    def test_zero_decodes_to_zero_stake(self, action_codec):
        x = np.zeros(len(action_codec.slots), dtype=np.int64)
        bets = action_codec.decode(x)
        for _, bet in iter_bets(bets):
            assert bet.stake == 0

    def test_one_decodes_to_min_stake(self, action_codec):
        x = np.zeros(len(action_codec.slots), dtype=np.int64)
        x[0] = 1  # pass_line
        bets = action_codec.decode(x)
        assert bets.pass_line.stake == TABLE_MIN


class TestNValues:
    def test_length_matches_slots(self, action_codec):
        n = action_codec.n_values()
        assert len(n) == len(action_codec.slots)

    def test_all_positive(self, action_codec):
        for nv in action_codec.n_values():
            assert nv >= 2  # at least 0 (no bet) and min stake