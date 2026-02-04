from abc import ABC, abstractmethod
from typing import Callable, Tuple
from typing import Optional
from craps.phase import TablePhase, transition_phase
from craps.dice import Roll

class Bet(ABC):
    def __init__(self, init_phase: TablePhase):
        self._phase = init_phase

    @property
    @abstractmethod
    def is_prop(self) -> bool:
        """Return True if this is a prop bet (uses prop_min instead of table_min)."""
        raise NotImplementedError

    def set_stake(self, amount: float, target: Optional[None]=None):
        """Set the stake amount for this bet."""
        if amount < 0.0:
            raise ValueError(f"Cannot set negative stake amount.")
        self._set_stake(amount, target=target)
    
    def get_stake(self, target: Optional[None]=None) -> float:
        """Get the current stake amount for this bet."""
        # No additional logic here. Just abstracting to _get_stake() for API consitency in the child class.
        return self._get_stake(target=target)

    def set_odds(self, amount: float, target: Optional[None]=None):
        """Set the odds amount for this bet."""
        if amount < 0.0:
            raise ValueError(f"Cannot set negative odds amount.")
        self._set_odds(amount, target=target)
    
    def get_odds(self, target: Optional[None]=None) -> float:
        """Get the current odds amount for this bet."""
        # No additional logic here. Just abstracting to _get_odds() for API consitency in the child class.
        return self._get_odds(target=target)
    
    def settle(self, roll: Roll) -> float:
        """Settle the bet for the given roll and advance the internal phase.

        Resolves the bet against the current phase, then transitions the
        phase using the roll.

        Returns:
            The total payout, or 0.0 on a loss/no-action.
        """
        result = self._settle(roll)
        self._phase = transition_phase(self._phase, roll)
        return result
    
    @abstractmethod
    def set_stake_targets(self) -> Tuple[Optional[int]]:
        raise NotImplementedError
    
    @abstractmethod
    def get_stake_targets(self) -> Tuple[Optional[int]]:
        raise NotImplementedError
    
    @abstractmethod
    def set_odds_targets(self) -> Tuple[Optional[int]]:
        raise NotImplementedError
    
    @abstractmethod
    def get_odds_targets(self) -> Tuple[Optional[int]]:
        raise NotImplementedError

    @abstractmethod
    def get_stake_increment(self, target: Optional[int] = None) -> int:
        """Return the casino-friendly increment for stake bets."""
        raise NotImplementedError

    @abstractmethod
    def get_odds_increment(self, target: Optional[int] = None) -> Optional[int]:
        """Return the casino-friendly increment for odds bets, or None if odds not supported."""
        raise NotImplementedError

    @abstractmethod
    def _set_stake(self, amount: float, target: Optional[None]=None):
        """Internal method to set stake. Implemented by subclasses."""
        raise NotImplementedError

    @abstractmethod
    def _get_stake(self, target: Optional[None]=None) -> float:
        """Internal method to get stake. Implemented by subclasses."""
        raise NotImplementedError

    @abstractmethod
    def _set_odds(self, amount: float, target: Optional[None]=None):
        """Internal method to set odds. Implemented by subclasses."""
        raise NotImplementedError

    @abstractmethod
    def _get_odds(self, target: Optional[None]=None) -> float:
        """Internal method to get odds. Implemented by subclasses."""
        raise NotImplementedError
    
    @abstractmethod
    def _settle(self, roll: Roll) -> float:
        """Settle the bet against the current phase. Called before phase is updated."""
        raise NotImplementedError

def requires_target(allowed: Tuple[int]):
    def decorator(fn: Callable):
        def wrapper(self, *args, **kwargs):
            target = kwargs.get("target")
            if target is None:
                raise ValueError(f"A value for 'target' must be provided.")
            if target not in allowed:
                raise ValueError(f"'target' must be one of: {','.join(str(a) for a in allowed)}. Got: {target}")
            return fn(self, *args, **kwargs)
        return wrapper
    return decorator

def forbids_target(fn: Callable):
    def wrapper(self, *args, **kwargs):
        if kwargs.get("target") is not None:
            raise ValueError(f"A value for 'target' was provided but the method does not use the 'target' kwarg.")
        return fn(self, *args, **kwargs)
    return wrapper

def forbids_odds__do_not_call(fn: Callable):
    def wrapper(self, *args, **kwargs):
        raise RuntimeError(f"This bet does not have odds.")
    return wrapper
