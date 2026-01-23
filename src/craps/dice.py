class Roll(tuple):
    """
    Represents the roll of 2 six-sided dice.
    """
    __slots__ = ()

    def total(self) -> int:
        """
        Returns the dice total.
        """
        return self[0] + self[1]
