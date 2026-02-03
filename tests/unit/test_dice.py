from hypothesis import given
from hypothesis.strategies import integers
from craps.dice import Roll


@given(
    die1=integers(min_value=1, max_value=6),
    die2=integers(min_value=1, max_value=6)
)
def test_roll_total(die1, die2):
    """Test that Roll.total() correctly sums the two dice."""
    roll = Roll((die1, die2))
    assert roll.total() == die1 + die2
