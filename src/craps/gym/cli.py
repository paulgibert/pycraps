"""
Tiny CLI for manually playing the craps gym.

Commands:
    bet <name> <amount>   Set a bet to an absolute stake (0 to remove)
    roll                  Submit current bets and roll the dice
    leave                 Leave the table
    info                  Show table limits and available bet names
    bets                  Show your current staged bets
    help                  Show this help
    quit                  Exit the CLI
"""
import numpy as np
from craps.bets.model import ActionBets, iter_bets
from craps.gym.env import CrapsEnv


def _bet_names() -> list[str]:
    return [name for name, _ in iter_bets(ActionBets())]


def _build_action(env: CrapsEnv, staged: dict[str, int], leave: bool) -> np.ndarray:
    action = np.zeros(env.action_space.shape, dtype=np.int64)
    action[0] = int(leave)
    for i, sc in enumerate(env._action_codec.slots):
        stake = staged.get(sc.slot, 0)
        if stake == 0:
            action[i + 1] = 0
        else:
            action[i + 1] = (stake - sc.min_stake) // sc.increment + 1
    return action


def _sync_staged(env: CrapsEnv, staged: dict[str, int]):
    """Sync staged bets with the actual table state after a roll."""
    for name, bet in iter_bets(env._table_state.bets):
        if name not in {sc.slot for sc in env._action_codec.slots}:
            continue
        if bet.stake == 0:
            staged.pop(name, None)
        else:
            staged[name] = bet.stake


def main():
    env = CrapsEnv(render_mode='human')
    env.reset()

    valid_names = set(_bet_names())
    slot_configs = {sc.slot: sc for sc in env._action_codec.slots}
    staged: dict[str, int] = {}

    print(f'Welcome to the craps table! Bankroll: ${env.init_bankroll}')
    print('Type "help" for commands.\n')

    while True:
        try:
            line = input('> ').strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not line:
            continue

        parts = line.split()
        cmd = parts[0].lower()

        if cmd == 'help':
            print(__doc__)

        elif cmd == 'info':
            print(f'Table min:  ${env.table_min}')
            print(f'Table max:  ${env.table_max}')
            print(f'Prop min:   ${env.prop_min}')
            print(f'Max odds:   {env.max_odds}x')
            print(f'Bet names:  {", ".join(_bet_names())}')

        elif cmd == 'bets':
            if not staged:
                print('No bets staged.')
            else:
                for name, amount in staged.items():
                    print(f'  {name}: ${amount}')

        elif cmd == 'bet':
            if len(parts) != 3:
                print('Usage: bet <name> <amount>')
                continue
            name = parts[1]
            if name not in valid_names:
                print(f'Unknown bet: {name}')
                print(f'Valid: {", ".join(sorted(valid_names))}')
                continue
            try:
                amount = int(parts[2])
            except ValueError:
                print('Amount must be an integer.')
                continue
            if amount < 0:
                print('Amount cannot be negative.')
                continue
            if amount == 0:
                staged.pop(name, None)
                print(f'{name} cleared')
                continue
            sc = slot_configs[name]
            if amount < sc.min_stake:
                print(f'{name} minimum is ${sc.min_stake}')
                continue
            if amount > sc.max_stake:
                print(f'{name} maximum is ${sc.max_stake}')
                continue
            if (amount - sc.min_stake) % sc.increment != 0:
                print(f'{name} must be ${sc.min_stake} + multiples of ${sc.increment}')
                continue
            staged[name] = amount
            print(f'{name} set to ${amount}')

        elif cmd == 'roll':
            action = _build_action(env, staged, leave=False)
            _, reward, terminated, _, _ = env.step(action)
            env.render()
            if reward < 0:
                print(f'Reward: {reward}')
            _sync_staged(env, staged)
            if terminated:
                print('Game over.')
                break

        elif cmd == 'leave':
            action = _build_action(env, staged, leave=True)
            _, _, terminated, _, _ = env.step(action)
            env.render()
            print('Left the table.')
            break

        elif cmd == 'quit':
            break

        else:
            print(f'Unknown command: {cmd}. Type "help" for commands.')


if __name__ == '__main__':
    main()
