from dataclasses import dataclass

@dataclass
class CrapsEnvConfig:
    init_bankroll: float
    max_bankroll: float
    max_points: int
    min_bet_inc: int
    entertainment_cost: float = 0.0
    illegal_action_penalty: float = 0.01