from sb3_contrib import MaskablePPO
import wandb
from wandb.integration.sb3 import WandbCallback
from craps.gym.env import CrapsEnv
from craps.gym.config import CrapsEnvConfig
from craps.gym.wrappers import FlattenActionWrapper, CPTBuffer, CPTRewardWrapper
from craps.state import TableConfig
from craps.phase import TablePhase
from craps.bets import PassLine, PlaceBets, Field, ComeBets

def main():
    # Configure environment
    env_config = CrapsEnvConfig(
        init_bankroll=1000.0,
        max_rolls=100,
        max_steps=100,
        min_increment=5
    )
    table_config = TableConfig(
        table_min=15,
        table_max=75,
        odds_max=3,
        prop_min=5
    )

    # Initialize bets
    init_phase = TablePhase()
    bets = {
        'pass_line': PassLine(init_phase),
        'come': ComeBets(init_phase),
        'place': PlaceBets(init_phase),
        'field': Field(init_phase),
    }

    # Create environment
    env = FlattenActionWrapper(CrapsEnv(env_config, table_config, bets))
    
    buffer = CPTBuffer(100)
    env = CPTRewardWrapper(env, buffer)
    
    # Create agent
    model = MaskablePPO("MultiInputPolicy", env, verbose=1)

    # Train agent
    wandb.init(project="craps-rl")
    model.learn(
        5_000_000,
        callback=WandbCallback(
            gradient_save_freq=1000,
            model_save_path="models/",
            model_save_freq=50_000,
            verbose=2
        )
    )

if __name__ == '__main__':
    main()