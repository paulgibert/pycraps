from abc import ABC, abstractmethod
from typing import Callable, Tuple
from typing import Optional
from craps.phase import TablePhase
from craps.dice import Roll

class Bet(ABC):
    def set_stake(self, amount: float, target: Optional[None]=None):
        """
        # TODO
        """
        if amount < 0.0:
            raise ValueError(f"Cannot set stake amount to zero.")
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
            raise ValueError(f"Cannot set stake amount to zero.")
        self._set_odds(amount, target=target)
    
    def get_odds(self, target: Optional[None]=None) -> float:
        """
        # TODO
        """
        # No additional logic here. Just abstracting to _get_odds() for API consitency in the child class.
        return self._get_odds(target=target)
    
    def settle(self, phase: TablePhase, roll: Roll) -> float:
        """
        # TODO
        """
        # No additional logic here. Just abstracting to _settle() for API consitency in the child class.
        return self._settle(phase, roll)
    
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
    def _settle(self, phase: TablePhase, roll: Roll) -> float:
        """
        # TODO
        """
        raise NotImplementedError

def requires_target(allowed: Tuple[int]):
    def decorator(fn: Callable):
        def wrapper(self, *args, **kwargs):
            target = kwargs.get("target")
            if target is None:
                raise ValueError(f"A value for 'target' must be provided.")
            if target not in allowed:
                raise ValueError(f"'target' must be one of: {','.join(allowed)}. Got: {target}")
            fn()
        return wrapper
    return decorator

def forbids_target(fn: Callable):
    def wrapper(self, *args, **kwargs):
        if kwargs.get("target") is not None:
            raise ValueError(f"A value for 'target' was provided but the method does not use the 'target' kwarg.")
        fn()
    return wrapper

def forbids_odds__do_not_call(fn: Callable):
    def wrapper(self, *args, **kwargs):
        raise RuntimeError(f"This bet does not have odds.")
    return wrapper
