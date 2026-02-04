#!/usr/bin/env python
"""Validate CrapsEnv compatibility with Stable Baselines3."""

from stable_baselines3.common.env_checker import check_env

from craps.gym.env import CrapsEnv
from craps.gym.config import CrapsEnvConfig
from craps.gym.wrappers import FlattenActionWrapper
from craps.state import TableConfig
from craps.phase import TablePhase
from craps.bets import PassLine, PlaceBets, Field


def main():
    # Configure environment
    env_config = CrapsEnvConfig(
        init_bankroll=1000.0,
        max_rolls=100,
        max_steps=100,
        min_increment=5
    )
    table_config = TableConfig(
        table_min=10,
        table_max=500,
        odds_max=100,
        prop_min=5
    )

    # Initialize bets
    init_phase = TablePhase()
    bets = {
        'pass_line': PassLine(init_phase),
        'place': PlaceBets(init_phase),
        'field': Field(init_phase),
    }

    # Create environment
    env = FlattenActionWrapper(CrapsEnv(env_config, table_config, bets))

    # Run SB3 compatibility check
    print("Running check_env...")
    check_env(env)
    print("check_env passed!")


if __name__ == "__main__":
    main()