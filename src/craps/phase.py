from typing import Optional, Dict, Iterator, Tuple
from dataclasses import dataclass, replace
from craps.dice import Roll
from craps.constants import POINTS, SEVEN_OUT
from craps.registry import BETS_REGISTRY

@dataclass
class TablePhase:
    """
    Represents the phase of the table, such as the point and value of stateful bets.
    """
    point: Optional[int]=None
    pass_line: int=0
    come_bets: Dict[int: bool]={n: False for n in POINTS}
    dont_come_bets: Dict[int: bool]={n: False for n in POINTS}

def transition_phase(phase: TablePhase, roll: Roll) -> TablePhase:
    total = roll.total()

    # Comeout: establish point
    if phase.point is None and total in POINTS:
        return replace(phase, point=total)

    # Point on: clear point on hit or seven-out
    if phase.point is not None and total in (phase.point, SEVEN_OUT):
        return replace(phase, point=None)

    # Otherwise no change to phase
    return replace(phase)
