from craps.exceptions import InsufficientFunds

#TODO: Add performance tracking

class Bankroll:
    """
    An object to manage a bankroll. Useful for catching actions that
    cost more than the available bankroll.
    """
    def __init__(self, init_bankroll: int):
        if init_bankroll < 0:
            raise ValueError(f"Cannot initialize bankroll to a negative value.")
        self._size = init_bankroll
    
    def update(self, amount: int):
        """
        If amount is negative, withdraws from the bankroll.
        If amount is positive, deposits to the bankroll.
        """
        if amount < 0:
            self.withdraw(-amount)
        elif amount > 0:
            self.deposit(amount)
        # else: do nothing
        
    def deposit(self, amount: int):
        """
        Adds funds to the bankroll.
        """
        if amount < 0:
            raise ValueError(f"Cannot deposit a negative amount.")
        self._size += amount
    
    def withdraw(self, amount: int):
        """
        Subtracts funds from the bankroll. Throw an exception if there are not enough funds.
        """
        if amount < 0:
            raise ValueError(f"Cannot withdraw a negative amount.")
        if amount > self._size:
            raise InsufficientFunds(f"Not enough funds.")
        self._size -= amount
    
    def get_size(self) -> int:
        """
        Returns the size of the bankroll.
        """
        return self._size
