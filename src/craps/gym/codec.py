from dataclasses import dataclass

import numpy as np

from craps.bets.model import iter_bets, set_stake


@dataclass(frozen=True)
class SlotConfig:
    """Pre-computed config for one bet slot in the MultiDiscrete space."""
    slot: str
    bet_type: type
    increment: int
    min_stake: int
    max_stake: int
    n_values: int  # number of discrete values including 0 (no bet)


class BetCodec:
    """
    Encodes/decodes between numpy action vectors and ActionBets/StateBets.

    Encoding scheme per slot:
        0 = no bet
        1 = min_stake
        2 = min_stake + increment
        ...
    """

    def __init__(
        self,
        bets_type: type,
        table_min: int,
        table_max: int,
        prop_min: int,
    ):
        self.bets_type = bets_type
        self.slots: list[SlotConfig] = []

        for slot, bet in iter_bets(bets_type()):
            inc = max(bet.increment)
            raw_min = prop_min if bet.is_prop else table_min
            # Round up to next valid increment
            min_stake = ((raw_min + inc - 1) // inc) * inc
            n_valid = len(range(min_stake, table_max + 1, inc))
            self.slots.append(SlotConfig(
                slot=slot,
                bet_type=type(bet),
                increment=inc,
                min_stake=min_stake,
                max_stake=table_max,
                n_values=n_valid + 1,  # +1 for the 0 (no bet) value
            ))

    def n_values(self) -> list[int]:
        """Discrete dimension sizes for building a MultiDiscrete space."""
        return [s.n_values for s in self.slots]

    def encode(self, bets) -> np.ndarray:
        """Bets dataclass -> numpy array. 0 = no bet, 1 = min, 2 = min+inc, ..."""
        vec = []
        for sc, (_, bet) in zip(self.slots, iter_bets(bets)):
            if bet.stake == 0:
                vec.append(0)
            else:
                vec.append((bet.stake - sc.min_stake) // sc.increment + 1)
        return np.array(vec, dtype=np.int64)

    def decode(self, x: np.ndarray):
        """Numpy array -> bets dataclass. Inverse of encode."""
        bets = self.bets_type()
        for i, sc in enumerate(self.slots):
            if x[i] == 0:
                stake = 0
            else:
                stake = (int(x[i]) - 1) * sc.increment + sc.min_stake
            bets = set_stake(bets, sc.slot, stake)
        return bets