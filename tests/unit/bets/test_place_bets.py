import pytest
from craps.dice import Roll
from craps.phase import TablePhase, transition_phase
from craps.bets.place_bets import PlaceBets
from craps.constants import POINTS
from craps.exceptions import IllegalAction

POINT_ROLLS = [Roll((2, 2)), Roll((2, 3)), Roll((1, 5)), Roll((2, 6)), Roll((5, 4)), Roll((5, 5))]

@pytest.fixture
def comeout():
    return TablePhase(point=None)

@pytest.fixture
def point_on_6(comeout):
    return transition_phase(comeout, Roll((3, 3)))

def test_settle_comeout_roll_7_but_off(point_on_6: TablePhase):
    place = PlaceBets(point_on_6)
    # Place on the 4
    place.set_stake(30.0, target=4)

    # Hit the point, back to come-out, place bets go off
    place.settle(Roll((3,3)))

    # Roll a 7
    assert place.settle(Roll((3,4))) == 0.0
    assert place.get_stake(target=4) == 30.0

def test_settle_comeout_place_number_hit_but_off(point_on_6: TablePhase):
    place = PlaceBets(point_on_6)
    # Place on the 4
    place.set_stake(30.0, target=4)

    # Hit the point, back to come-out, place bets go off
    place.settle(Roll((3,3)))

    # Roll a 4
    assert place.settle(Roll((3,1))) == 0.0
    assert place.get_stake(target=4) == 30.0

def test_settle_seven_out_clears_everything(point_on_6: TablePhase):
    place = PlaceBets(point_on_6)
    # Place every number
    for tgt in POINTS:
        place.set_stake(30.0, target=tgt)

    # Seven-out
    assert place.settle(Roll((3,4))) == 0.0

    for tgt in POINTS:
        assert place.get_stake(target=tgt) == 0.0

@pytest.mark.parametrize(
    "roll, winnings",
    [
        (Roll((2,2)), 54.0),
        (Roll((2,3)), 42.0),
        (Roll((3,3)), 35.0),
        (Roll((4,4)), 35.0),
        (Roll((5,4)), 42.0),
        (Roll((5,5)), 54.0)
    ]
)
def test_settle_place_number_is_rolled(roll: Roll, winnings: float, point_on_6: TablePhase):
    place = PlaceBets(point_on_6)
    # Place a number
    number = roll.total()
    place.set_stake(30.0, target=number)
    # Roll the number
    assert place.settle(roll) == winnings
    assert place.get_stake(target=number) == 30.0

def test_set_stake_without_target_errors(point_on_6: TablePhase):
    place = PlaceBets(point_on_6)
    with pytest.raises(ValueError):
        place.set_stake(30.0, target=None)

def test_set_stake_errors_on_bad_target(point_on_6: TablePhase):
    place = PlaceBets(point_on_6)
    with pytest.raises(ValueError):
        place.set_stake(30.0, target=12)

def test_set_stake_errors_on_comeout(comeout: TablePhase):
    place = PlaceBets(comeout)
    with pytest.raises(IllegalAction):
        place.set_stake(30.0, target=6)

@pytest.mark.parametrize("number", POINTS)
def test_set_and_get_stake_work(number: int, point_on_6: TablePhase):
    place = PlaceBets(point_on_6)
    place.set_stake(30.0, target=number)
    assert place.get_stake(target=number) == 30.0

def test_get_stake_without_target_errors(point_on_6: TablePhase):
    place = PlaceBets(point_on_6)
    with pytest.raises(ValueError):
        place.get_stake(target=None)

def test_set_odds_always_errors(point_on_6: TablePhase):
    place = PlaceBets(point_on_6)
    place.set_stake(30.0, target=6)
    with pytest.raises(RuntimeError):
        place.set_odds(60.0, target=6)

def test_get_odds_always_errors(point_on_6: TablePhase):
    place = PlaceBets(point_on_6)
    with pytest.raises(RuntimeError):
        place.get_odds(target=6)


def test_reset_clears_all_stakes(point_on_6: TablePhase):
    place = PlaceBets(point_on_6)
    for tgt in POINTS:
        place.set_stake(30.0, target=tgt)
    place.reset()
    for tgt in POINTS:
        assert place.get_stake(target=tgt) == 0.0
    assert place._phase.point is None
