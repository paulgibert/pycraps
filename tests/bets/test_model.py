import pytest
from craps.bets.model import StateBets, set_stake


def test_set_stake_pass_line():
    """Test that set_stake updates pass_line correctly."""
    bets = StateBets()
    bets = set_stake(bets, 'pass_line', 10)

    new_bets = set_stake(bets, 'pass_line', 20)

    assert new_bets.pass_line.stake == 20
    assert bets.pass_line.stake == 10  # Original unchanged (immutable)


def test_set_stake_unknown_slot():
    """Test that set_stake raises AttributeError for unknown slot."""
    bets = StateBets()

    with pytest.raises(AttributeError):
        set_stake(bets, 'unknown_slot', 20)


def test_iter_bets():
    """Test that iter_bets yields correct tuples for all fields."""
    #TODO
    pass


def test_iter_bets_zero():
    """Test that iter_bets yields zero stakes for all fields."""
    # TODO
    pass
