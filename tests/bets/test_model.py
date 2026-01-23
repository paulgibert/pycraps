import pytest
from craps.bets.model import Bets, set_bets, iter_bets


def test_set_bets_pass_line():
    """Test that set_bets updates pass_line correctly."""
    bets = Bets(pass_line=10)

    new_bets = set_bets(bets, 'pass_line', 20)

    assert new_bets.pass_line == 20
    assert bets.pass_line == 10  # Original unchanged (immutable)


def test_set_bets_unknown_slot():
    """Test that set_bets raises KeyError for unknown slot."""
    bets = Bets(pass_line=10)

    with pytest.raises(KeyError):
        set_bets(bets, 'unknown_slot', 20)


def test_iter_bets():
    """Test that iter_bets yields correct tuples."""
    bets = Bets(pass_line=10, pass_odds=5)

    result = list(iter_bets(bets))

    assert result == [('pass_line', 10), ('pass_odds', 5)]


def test_iter_bets_zero():
    """Test that iter_bets yields zero stakes."""
    bets = Bets()  # All defaults to zero

    result = list(iter_bets(bets))

    assert result == [('pass_line', 0), ('pass_odds', 0)]
