from dataclasses import dataclass

@dataclass
class CrapsEnvConfig:
    init_bankroll: float
    max_rolls: int
    max_steps: int
    min_increment: int
