from abc import ABC, abstractmethod
from typing import Callable, Tuple
from typing import Optional
from craps.phase import TablePhase, transition_phase
from craps.dice import Roll

class Bet(ABC):
    def __init__(self, init_phase: TablePhase):
        self._phase = init_phase
    
    def set_stake(self, amount: float, target: Optional[None]=None):
        """
        # TODO
        """
        if amount < 0.0:
            raise ValueError(f"Cannot set negative stake amount.")
        self._set_stake(amount, target=target)
    
    def get_stake(self, target: Optional[None]=None) -> float:
        """
        # TODO
        """
        # No additional logic here. Just abstracting to _get_stake() for API consitency in the child class.
        return self._get_stake(target=target)

    def set_odds(self, amount: float, target: Optional[None]=None):
        """
        # TODO
        """
        if amount < 0.0:
            raise ValueError(f"Cannot set negative odds amount.")
        self._set_odds(amount, target=target)
    
    def get_odds(self, target: Optional[None]=None) -> float:
        """
        # TODO
        """
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
    def _set_stake(self, amount: float, target: Optional[None]=None):
        """
        # TODO
        """
        raise NotImplementedError

    @abstractmethod
    def _get_stake(self, target: Optional[None]=None) -> float:
        """
        # TODO
        """
        raise NotImplementedError

    @abstractmethod
    def _set_odds(self, amount: float, target: Optional[None]=None):
        """
        # TODO
        """
        raise NotImplementedError

    @abstractmethod
    def _get_odds(self, target: Optional[None]=None) -> float:
        """
        # TODO
        """
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
