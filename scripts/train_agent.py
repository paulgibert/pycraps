import argparse
from sb3_contrib import MaskablePPO
from stable_baselines3.common.vec_env import SubprocVecEnv
from stable_baselines3.common.callbacks import BaseCallback
import wandb
from wandb.integration.sb3 import WandbCallback
from craps.gym.env import CrapsEnv
from craps.gym.config import CrapsEnvConfig
from craps.gym.wrappers import FlattenActionWrapper, CPTBuffer, CPTRewardWrapper
from craps.state import TableConfig
from craps.phase import TablePhase
from craps.bets import PassLine, PlaceBets, Field, ComeBets

N_ENVS = 8


class CrapsMetricsCallback(BaseCallback):
    def _on_step(self):
        for info in self.locals["infos"]:
            if "ep_reward_total" in info:
                wandb.log({
                    "reward/total": info["ep_reward_total"],
                    "reward/cpt_delta": info["ep_cpt_delta"],
                    "reward/cpt_utility": info["ep_cpt_utility"],
                    "session/terminal_bankroll": info["terminal_bankroll"],
                    "session/total_steps": info["total_steps"],
                    "session/n_points": info["n_points"],
                    "session/illegal_actions": info["ep_illegal_actions"],
                    "session/adjusted_ref": info["adjusted_ref"],
                    "session/fractional_return": info["fractional_return"],
                })
        return True


def make_env(env_config, table_config, seed):
    def _init():
        init_phase = TablePhase()
        bets = {
            'pass_line': PassLine(init_phase),
            'come': ComeBets(init_phase),
            'place': PlaceBets(init_phase),
            'field': Field(init_phase),
        }
        env = FlattenActionWrapper(CrapsEnv(env_config, table_config, bets))
        buffer = CPTBuffer()
        env = CPTRewardWrapper(
            env, buffer,
            init_bankroll=env_config.init_bankroll,
            entertainment_cost=env_config.entertainment_cost
        )
        env.reset(seed=seed)
        return env
    return _init


def main():
    # Configure environment
    env_config = CrapsEnvConfig(
        init_bankroll=1000.0,
        max_bankroll=2000.0,
        max_points=30,
        min_bet_inc=5,
        entertainment_cost=5.0,
    )
    table_config = TableConfig(
        table_min=15,
        table_max=75,
        odds_max=3,
        prop_min=5
    )

    # Create vectorized environment
    env = SubprocVecEnv([make_env(env_config, table_config, seed=i) for i in range(N_ENVS)])

    # Create or load agent
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", type=str, default=None, help="Path to a saved model zip to resume from")
    args = parser.parse_args()

    if args.resume:
        model = MaskablePPO.load(args.resume, env=env)
    else:
        model = MaskablePPO("MultiInputPolicy", env, verbose=1)

    # Train agent
    wandb.init(project="craps-rl")
    model.learn(
        5_000_000,
        callback=[
            WandbCallback(
                gradient_save_freq=0,
                model_save_path="models/",
                model_save_freq=50_000,
                verbose=2
            ),
            CrapsMetricsCallback(),
        ]
    )

if __name__ == '__main__':
    main()