import pytest
from craps.phase import TablePhase
from craps.dice import Roll
from craps.bets import Field

FIELD_WINNERS = [Roll((1, 2)), Roll((2, 2)), Roll((4, 5)), Roll((5, 5)), Roll((5, 6))]
FIELD_LOSERS = [Roll((3, 4)), Roll((2, 3)), Roll((1, 5)), Roll((2, 6)), Roll((4, 4))]

@pytest.fixture(params=[None, 6], ids=["comeout", "point_on_6"])
def phase(request):
    return TablePhase(point=request.param)

def test_settle_2(phase: TablePhase):
    field = Field(phase)
    field.set_stake(30.0)
    assert field.settle(Roll((1, 1))) == 90.0
    assert field.get_stake() == 0.0

def test_settle_12(phase: TablePhase):
    field = Field(phase)
    field.set_stake(30.0)
    assert field.settle(Roll((6, 6))) == 120.0
    assert field.get_stake() == 0.0

@pytest.mark.parametrize("roll", FIELD_WINNERS)
def test_settle_other_winner(roll: Roll, phase: TablePhase):
    field = Field(phase)
    field.set_stake(30.0)
    assert field.settle(roll) == 60.0
    assert field.get_stake() == 0.0

@pytest.mark.parametrize("roll", FIELD_LOSERS)
def test_settle_loser(roll: Roll, phase: TablePhase):
    field = Field(phase)
    field.set_stake(30.0)
    assert field.settle(roll) == 0.0
    assert field.get_stake() == 0.0

def test_set_and_get_stake_work(phase: TablePhase):
    field = Field(phase)
    field.set_stake(30.0)
    assert field.get_stake() == 30.0

def test_set_stake_with_target_errors(phase: TablePhase):
    field = Field(phase)
    with pytest.raises(ValueError):
        field.set_stake(30.0, target=10)

def test_get_stake_with_target_errors(phase: TablePhase):
    field = Field(phase)
    field.set_stake(30.0)
    with pytest.raises(ValueError):
        field.get_stake(target=10)

def test_set_odds_errors(phase: TablePhase):
    field = Field(phase)
    field.set_stake(30.0)
    with pytest.raises(RuntimeError):
        field.set_odds(60.0)

def test_get_odds_errors(phase: TablePhase):
    field = Field(phase)
    with pytest.raises(RuntimeError):
        field.get_odds()
