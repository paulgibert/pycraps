from pprint import pprint
from stable_baselines3 import PPO
from craps.gym.env import CrapsEnv
from craps.gym.config import CrapsEnvConfig
from craps.gym.wrappers import FlattenActionWrapper
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
        table_max=500,
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

    model = PPO.load("model_ppo.zip")

    obs, _ = env.reset()
    while True:
        action, _ = model.predict(obs, deterministic=True)
        breakpoint()
        obs, reward, done, truncated, info = env.step(action)
        render_out = env.render()
        pprint(render_out)
        
        if done or truncated:
            break

        text = input()
        if text == "quit":
            break

if __name__ == "__main__":
    main()
