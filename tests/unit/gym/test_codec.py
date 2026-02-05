from typing import Optional
import pytest
from craps.bets.model import Bet,requires_target
from craps.phase import TablePhase
from craps.dice import Roll
from craps.state import TableConfig
from craps.gym.codec import BetCodec

ALL_NUMBERS = list(range(2, 13))

class DummyBet(Bet):
    """A dummy bet implementation for testing TableState."""
    def __init__(self, init_phase: TablePhase):
        super().__init__(init_phase)
        self._stake = {n: 0.0 for n in range(2, 13)}
        self._odds = {n: 0.0 for n in range(2, 13)}

    @property
    def is_prop(self) -> bool:
        return False

    def _settle(self, roll: Roll):
        total = roll.total()
        return self._stake[total] + self._odds[total]

    @requires_target(ALL_NUMBERS)
    def _set_stake(self, amount: float, target: Optional[int] = None):
        self._stake[target] = amount

    @requires_target(ALL_NUMBERS)
    def _get_stake(self, target: Optional[int] = None) -> float:
        return self._stake[target]

    @requires_target(ALL_NUMBERS)
    def _set_odds(self, amount: float, target: Optional[int] = None):
        self._odds[target] = amount

    @requires_target(ALL_NUMBERS)
    def _get_odds(self, target: Optional[int] = None) -> float:
        return self._odds[target]

    def get_stake_targets(self):
        return tuple(ALL_NUMBERS)

    def set_stake_targets(self):
        return tuple(ALL_NUMBERS)

    def get_odds_targets(self):
        return tuple(ALL_NUMBERS)

    def set_odds_targets(self):
        return tuple(ALL_NUMBERS)

    @requires_target(ALL_NUMBERS)
    def get_stake_increment(self, target: Optional[int] = None) -> int:
        return 6

    @requires_target(ALL_NUMBERS)
    def get_odds_increment(self, target: Optional[int] = None) -> Optional[int]:
        return 6

    def can_set_stake(self, target=None) -> bool:
        return True

    def can_set_odds(self, target=None) -> bool:
        return True

class DummyPropBet(Bet):
    """A dummy prop bet implementation for testing TableState."""
    def __init__(self, init_phase: TablePhase):
        super().__init__(init_phase)
        self._stake = {n: 0.0 for n in range(2, 13)}
        self._odds = {n: 0.0 for n in range(2, 13)}

    @property
    def is_prop(self) -> bool:
        return True

    def _settle(self, roll: Roll):
        total = roll.total()
        return self._stake[total] + self._odds[total]

    @requires_target(ALL_NUMBERS)
    def _set_stake(self, amount: float, target: Optional[int] = None):
        self._stake[target] = amount

    @requires_target(ALL_NUMBERS)
    def _get_stake(self, target: Optional[int] = None) -> float:
        return self._stake[target]

    @requires_target(ALL_NUMBERS)
    def _set_odds(self, amount: float, target: Optional[int] = None):
        self._odds[target] = amount

    @requires_target(ALL_NUMBERS)
    def _get_odds(self, target: Optional[int] = None) -> float:
        return self._odds[target]

    def get_stake_targets(self):
        return tuple(ALL_NUMBERS)

    def set_stake_targets(self):
        return tuple(ALL_NUMBERS)

    def get_odds_targets(self):
        return tuple(ALL_NUMBERS)

    def set_odds_targets(self):
        return tuple(ALL_NUMBERS)

    @requires_target(ALL_NUMBERS)
    def get_stake_increment(self, target: Optional[int] = None) -> int:
        return 6

    @requires_target(ALL_NUMBERS)
    def get_odds_increment(self, target: Optional[int] = None) -> Optional[int]:
        return 6

    def can_set_stake(self, target=None) -> bool:
        return True

    def can_set_odds(self, target=None) -> bool:
        return True

@pytest.fixture
def table_config():
    return TableConfig(
        table_min=15.0,
        table_max=30.0,
        odds_max=3.0,
        prop_min=5.0
    )

@pytest.fixture
def codec(request, table_config: TableConfig) -> BetCodec:
    if request.param == "bet":
        return BetCodec(
            table_config,
            DummyBet(TablePhase(None)),
            min_increment=5,
        )
    elif request.param == "prop":
        return BetCodec(
            table_config,
            DummyPropBet(TablePhase(None)),
            min_increment=5,
        )
    else:
        raise ValueError(request.param)

class TestBetCodec:
    @pytest.mark.parametrize(
        "codec,size",
        [("bet", 4), ("prop", 6)],
        indirect=["codec"]
    )
    def test_get_stake_discrete_size(self, codec: BetCodec, size: int):
        assert codec.get_stake_discrete_size(target=2) == size

    @pytest.mark.parametrize(
        "codec,size",
        [("bet", 4), ("prop", 6)],
        indirect=["codec"]
    )
    def test_get_odds_discrete_size(self, codec: BetCodec, size: int):
        assert codec.get_odds_discrete_size(target=2) == size
    
    @pytest.mark.parametrize(
        "codec,x",
        [("bet", 1), ("prop", 3)],
        indirect=["codec"]
    )
    def test_stake_amount_to_discrete(self, codec: BetCodec, x: int):
        assert codec.stake_amount_to_discrete(18.0, target=4) == x
    
    @pytest.mark.parametrize(
        "codec,amount",
        [
            ("bet", 35.0),
            ("bet", -10.0),
            ("prop", 40.0),
            ("prop", -1.0)
        ],
        indirect=["codec"]
    )
    def test_stake_amount_to_discrete_oob(self, codec: BetCodec, amount: float):
        with pytest.raises(ValueError):
            assert codec.stake_amount_to_discrete(amount, target=4)
    
    @pytest.mark.parametrize(
        "codec,x",
        [("bet", 2), ("prop", 4)],
        indirect=["codec"]
    )
    def test_odds_amount_to_discrete(self, codec: BetCodec, x: int):
        assert codec.odds_amount_to_discrete(24.0, target=4) == x
    
    @pytest.mark.parametrize(
        "codec,amount",
        [
            ("bet", 35.0),
            ("bet", -10.0),
            ("prop", 40.0),
            ("prop", -1.0)
        ],
        indirect=["codec"]
    )
    def test_odds_amount_to_discrete_oob(self, codec: BetCodec, amount: float):
        with pytest.raises(ValueError):
            assert codec.odds_amount_to_discrete(amount, target=4)

    @pytest.mark.parametrize(
        "codec,amount",
        [("bet", 30.0), ("prop", 18.0)],
        indirect=["codec"]
    )
    def test_stake_discrete_to_amount(self, codec: BetCodec, amount: float):
        assert codec.stake_discrete_to_amount(3, target=4) == amount
    
    @pytest.mark.parametrize(
        "codec,x",
        [
            ("bet", 10),
            ("bet", -1),
            ("prop", 12),
            ("prop", -100)
        ],
        indirect=["codec"]
    )
    def test_stake_discrete_to_amount(self, codec: BetCodec, x: int):
        with pytest.raises(ValueError):
            assert codec.stake_discrete_to_amount(x, target=4)

    @pytest.mark.parametrize(
        "codec,amount",
        [("bet", 24.0), ("prop", 12.0)],
        indirect=["codec"]
    )
    def test_odds_discrete_to_amount(self, codec: BetCodec, amount: float):
        assert codec.odds_discrete_to_amount(2, target=4) == amount
    
    @pytest.mark.parametrize(
        "codec,x",
        [
            ("bet", 10),
            ("bet", -1),
            ("prop", 12),
            ("prop", -100)
        ],
        indirect=["codec"]
    )
    def test_odds_discrete_to_amount(self, codec: BetCodec, x: int):
        with pytest.raises(ValueError):
            assert codec.odds_discrete_to_amount(x, target=4)

# TODO: Add SpaceCodec tests
